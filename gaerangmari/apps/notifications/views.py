from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from common.pagination import StandardResultsSetPagination
from common.response import CustomResponse
from .models import Notification, WebPushSubscription
from .serializers import (
    NotificationBulkDeleteSerializer,
    NotificationListSerializer,
    NotificationSettingsUpdateSerializer,
    NotificationUpdateSerializer,
    WebPushSubscriptionSerializer,
)


class NotificationListView(generics.ListAPIView):
    """알림 목록 조회"""
    pagination_class = StandardResultsSetPagination
    serializer_class = NotificationListSerializer
    permission_classes = [IsAuthenticated]

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


class NotificationMarkReadView(APIView):
    """알림 읽음 처리"""
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id=None):
        if notification_id:
            # 단일 알림 읽음 처리
            notification = generics.get_object_or_404(
                Notification, id=notification_id, recipient=request.user
            )
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
        else:
            # 전체 알림 읽음 처리
            Notification.objects.filter(recipient=request.user, is_read=False).update(
                is_read=True, read_at=timezone.now()
            )

        return Response({"message": "알림이 읽음 처리되었습니다."}, status=status.HTTP_200_OK)



class NotificationBulkDeleteView(APIView):
    """알림 대량 삭제"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NotificationBulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get("delete_all"):
            # 전체 삭제
            Notification.objects.filter(recipient=request.user).delete()
        else:
            # 선택 삭제
            notification_ids = serializer.validated_data["notification_ids"]
            Notification.objects.filter(
                id__in=notification_ids, recipient=request.user
            ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationSettingsUpdateView(APIView):
    """알림 설정 업데이트"""
    permission_classes = [IsAuthenticated]

    def put(self, request):  # patch -> put으로 변경
        serializer = NotificationSettingsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        for field, value in serializer.validated_data.items():
            setattr(user, field, value)
        user.save()

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class WebPushSubscriptionView(APIView):
    """웹 푸시 구독 관리"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """구독 정보 등록/업데이트"""
        serializer = WebPushSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 400 에러는 자동으로 발생

        try:
            subscription, created = WebPushSubscription.objects.get_or_create(
                user=request.user,
                endpoint=serializer.validated_data['endpoint'],
                defaults={
                    'p256dh': serializer.validated_data['keys']['p256dh'],
                    'auth': serializer.validated_data['keys']['auth']
                }
            )

            if not created:
                # 기존 구독 정보 업데이트
                subscription.p256dh = serializer.validated_data['keys']['p256dh']
                subscription.auth = serializer.validated_data['keys']['auth']
                subscription.is_active = True
                subscription.save()

            return Response({
                "message": "웹 푸시 구독이 등록되었습니다.",
                "subscription_id": subscription.id
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """구독 취소"""
        endpoint = request.data.get('endpoint')
        if not endpoint:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        subscription = generics.get_object_or_404(
            WebPushSubscription,
            endpoint=endpoint,
            user=request.user
        )
        subscription.is_active = False
        subscription.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)