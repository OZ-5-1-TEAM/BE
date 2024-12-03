from pywebpush import webpush
from django.conf import settings
import json
from django.utils import timezone


def send_web_push_notification(user, title, body, data=None):
    """
    웹 푸시 알림 발송
    
    Args:
        user: 수신할 사용자 객체
        title: 알림 제목
        body: 알림 내용
        data: 추가 데이터 (딕셔너리)
    
    Returns:
        bool: 발송 성공 여부
    """
    if not user.push_enabled:
        return False

    subscriptions = user.push_subscriptions.filter(is_active=True)
    if not subscriptions:
        return False

    payload = {
        "notification": {
            "title": title,
            "body": body,
            "icon": "/static/images/notification-icon.png",  # 알림 아이콘 경로
            "badge": "/static/images/notification-badge.png",  # 알림 뱃지 경로
            "data": data or {}
        }
    }

    failed_endpoints = []
    success = False

    for subscription in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh,
                        "auth": subscription.auth
                    }
                },
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"
                }
            )
            success = True
        except Exception as e:
            failed_endpoints.append(subscription.endpoint)
            continue

    # 실패한 구독 정보 비활성화
    if failed_endpoints:
        user.push_subscriptions.filter(endpoint__in=failed_endpoints).update(
            is_active=False
        )

    return success


def update_notification_status(notification, status, error_message=None):
    """
    알림 발송 상태 업데이트
    
    Args:
        notification: Notification 객체
        status: 상태 ('sent' 또는 'failed')
        error_message: 실패 시 에러 메시지
    """
    notification.delivery_status = status
    if status == 'sent':
        notification.is_sent = True
        notification.sent_at = timezone.now()
    elif status == 'failed':
        notification.error_message = error_message

    notification.save()


def create_notification(
    recipient, notification_type, title, message, sender=None, content_object=None
):
    """
    알림 생성 및 푸시 발송
    
    Args:
        recipient: 수신자 (User 객체)
        notification_type: 알림 유형
        title: 알림 제목
        message: 알림 내용
        sender: 발신자 (User 객체, 선택사항)
        content_object: 관련 객체 (선택사항)
    
    Returns:
        Notification: 생성된 알림 객체
    """
    from .models import Notification  # 순환 참조 방지를 위해 여기서 임포트

    # 알림 생성
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        title=title,
        message=message,
        content_object=content_object,
    )

    # 푸시 알림 발송 시도
    if recipient.push_enabled:
        success = send_web_push_notification(
            user=recipient,
            title=title,
            body=message,
            data={
                "notification_id": notification.id,
                "type": notification_type,
            },
        )
        
        # 발송 상태 업데이트
        status = 'sent' if success else 'failed'
        update_notification_status(
            notification,
            status,
            error_message=None if success else "Push notification delivery failed"
        )

    return notification