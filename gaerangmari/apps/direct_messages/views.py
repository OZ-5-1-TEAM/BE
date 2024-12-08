# views.py
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from common.permissions import IsMessageParticipant
from common.pagination import StandardResultsSetPagination
from .models import Message
from .serializers import (
    MessageCreateSerializer,
    MessageDetailSerializer,
    MessageListSerializer,
    ReceivedMessageSerializer,
    SentMessageSerializer,
)


class MessageListCreateView(generics.ListCreateAPIView):
    """메시지 목록 조회 및 생성"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MessageCreateSerializer
        return MessageListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Message.objects.filter(
            Q(sender=user) | Q(receiver=user),
            is_deleted=False
        ).select_related("sender", "receiver")

        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(content__icontains=search) |
                Q(sender__nickname__icontains=search) |
                Q(receiver__nickname__icontains=search)
            )

        sort = self.request.query_params.get('sort', '-created_at')
        return queryset.order_by('-created_at' if sort != 'oldest' else 'created_at')


class ReceivedMessageListView(generics.ListAPIView):
    """받은 메시지 목록 조회"""
    serializer_class = ReceivedMessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Message.objects.filter(
            receiver=self.request.user,
            deleted_by_receiver=False,
            is_deleted=False
        ).select_related("sender")

        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(content__icontains=search) |
                Q(sender__nickname__icontains=search)
            )

        sort = self.request.query_params.get('sort', '-created_at')
        return queryset.order_by('-created_at' if sort != 'oldest' else 'created_at')


class SentMessageListView(generics.ListAPIView):
    """보낸 메시지 목록 조회"""
    serializer_class = SentMessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Message.objects.filter(
            sender=self.request.user,
            deleted_by_sender=False,
            is_deleted=False
        ).select_related("receiver")

        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(content__icontains=search) |
                Q(receiver__nickname__icontains=search)
            )

        sort = self.request.query_params.get('sort', '-created_at')
        return queryset.order_by('-created_at' if sort != 'oldest' else 'created_at')


class MessageReadView(APIView):
    """메시지 읽음 처리"""
    permission_classes = [IsAuthenticated]

    def put(self, request, message_id):
        try:
            message = Message.objects.get(
                id=message_id,
                receiver=request.user,
                is_deleted=False,
                deleted_by_receiver=False
            )
        except Message.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()

        serializer = MessageDetailSerializer(message)
        return Response(serializer.data)


class MessageDetailView(generics.RetrieveDestroyAPIView):
    """메시지 상세 조회 및 삭제"""
    serializer_class = MessageDetailSerializer
    permission_classes = [IsAuthenticated, IsMessageParticipant]
    lookup_url_kwarg = "message_id"

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user),
            is_deleted=False
        ).select_related("sender", "receiver")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.soft_delete(self.request.user)