from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import (
    FCMTokenSerializer,
    NotificationBulkDeleteSerializer,
    NotificationListSerializer,
    NotificationSerializer,
    NotificationSettingsUpdateSerializer,
)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    알림 관리를 위한 ViewSet
    생성/수정은 시스템에서 자동으로 처리되므로 ReadOnly로 설정
    """

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationListSerializer

    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user).order_by(
            "-created_at"
        )

        # 읽음 여부 필터
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)

        # 알림 타입 필터
        notification_type = self.request.query_params.get("type")
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        return queryset

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """단일 알림 읽음 처리"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({"message": "알림이 읽음 처리되었습니다."})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """전체 알림 읽음 처리"""
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({"message": "모든 알림이 읽음 처리되었습니다."})

    @action(detail=False, methods=["post"])
    def bulk_delete(self, request):
        """알림 대량 삭제"""
        serializer = NotificationBulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get("delete_all"):
            Notification.objects.filter(recipient=request.user).delete()
        else:
            notification_ids = serializer.validated_data["notification_ids"]
            Notification.objects.filter(
                id__in=notification_ids, recipient=request.user
            ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["patch"])
    def settings(self, request):
        """알림 설정 업데이트"""
        serializer = NotificationSettingsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        for field, value in serializer.validated_data.items():
            setattr(user, field, value)
        user.save()

        return Response(serializer.validated_data)

    @action(detail=False, methods=["post"])
    def register_token(self, request):
        """FCM 토큰 등록"""
        serializer = FCMTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # FCM 토큰 저장 로직 구현 필요

        return Response({"message": "FCM 토큰이 등록되었습니다."})
