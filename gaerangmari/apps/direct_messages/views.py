from common.permissions import IsMessageParticipant
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Message
from .serializers import (
    MessageCreateSerializer,
    MessageDeleteSerializer,
    MessageDetailSerializer,
    MessageListSerializer,
    MessageSerializer,
    ReceivedMessageSerializer,
    SentMessageSerializer,
)


class MessageListCreateView(generics.ListCreateAPIView):
    """쪽지 목록 조회 및 생성"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MessageCreateSerializer
        return MessageListSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user), is_deleted=False
        ).select_related("sender", "receiver")

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ReceivedMessageListView(generics.ListAPIView):
    """받은 쪽지함"""

    serializer_class = ReceivedMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            receiver=self.request.user, deleted_by_receiver=False, is_deleted=False
        ).select_related("sender")


class SentMessageListView(generics.ListAPIView):
    """보낸 쪽지함"""

    serializer_class = SentMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            sender=self.request.user, deleted_by_sender=False, is_deleted=False
        ).select_related("receiver")


class MessageDetailView(generics.RetrieveDestroyAPIView):
    """쪽지 상세 조회 및 삭제"""

    serializer_class = MessageDetailSerializer
    permission_classes = [IsAuthenticated, IsMessageParticipant]
    lookup_url_kwarg = "message_id"

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user), is_deleted=False
        )

    def perform_destroy(self, instance):
        instance.soft_delete(self.request.user)


class MessageReadView(APIView):
    """쪽지 읽음 처리"""

    permission_classes = [IsAuthenticated]

    def put(self, request, message_id):
        message = generics.get_object_or_404(
            Message, id=message_id, receiver=request.user, is_deleted=False
        )

        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()

        serializer = MessageDetailSerializer(message)
        return Response(serializer.data)


class MessageBulkDeleteView(generics.CreateAPIView):
    """쪽지 일괄 삭제"""

    serializer_class = MessageDeleteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        messages = Message.objects.filter(
            id__in=serializer.validated_data["message_ids"]
        )
        for message in messages:
            message.soft_delete(request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)
