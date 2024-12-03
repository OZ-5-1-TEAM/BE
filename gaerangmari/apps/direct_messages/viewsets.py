from django.db.models import Case, Count, IntegerField, Q, When
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        user = self.request.user
        base_queryset = (
            Message.objects.filter(Q(sender=user) | Q(receiver=user), is_deleted=False)
            .annotate(
                unread_count=Case(
                    When(receiver=user, is_read=False, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            )
            .select_related("sender", "receiver")
        )

        return base_queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # 수신자가 메시지를 읽을 때 읽음 처리
        if instance.receiver == request.user and not instance.is_read:
            instance.is_read = True
            instance.read_at = timezone.now()
            instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """읽지 않은 쪽지 수 조회"""
        count = (
            self.get_queryset()
            .filter(receiver=request.user, is_read=False, deleted_by_receiver=False)
            .count()
        )

        return Response({"unread_count": count})

    @action(detail=False, methods=["put"])
    def read_all(self, request):
        """모든 쪽지 읽음 처리"""
        messages = self.get_queryset().filter(
            receiver=request.user, is_read=False, deleted_by_receiver=False
        )

        update_count = messages.count()
        messages.update(is_read=True, read_at=timezone.now())

        return Response(
            {
                "message": f"{update_count}개의 쪽지를 읽음 처리했습니다.",
                "updated_count": update_count,
            }
        )

    @action(detail=False, methods=["get"])
    def conversation(self, request):
        """특정 사용자와의 대화 목록"""
        other_user_id = request.query_params.get("user_id")
        if not other_user_id:
            return Response(
                {"detail": "상대방 ID가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        messages = (
            self.get_queryset()
            .filter(
                Q(sender_id=other_user_id, receiver=request.user)
                | Q(sender=request.user, receiver_id=other_user_id)
            )
            .order_by("created_at")
        )

        serializer = MessageDetailSerializer(
            messages, many=True, context={"request": request}
        )
        return Response(serializer.data)
