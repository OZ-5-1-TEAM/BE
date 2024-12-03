from core.models import TimeStampedModel
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Notification(TimeStampedModel):
    """
    알림 모델
    """

    NOTIFICATION_TYPES = [
        ("message", "쪽지"),
        ("friend_request", "친구 요청"),
        ("friend_accept", "친구 수락"),
        ("comment", "댓글"),
        ("reply", "답글"),
        ("like", "좋아요"),
        ("system", "시스템"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sent_notifications",
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Generic Foreign Key for referenced object
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # 푸시 알림 관련
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=[("pending", "대기"), ("sent", "발송됨"), ("failed", "실패")],
        default="pending",
    )
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "알림"
        verbose_name_plural = "알림 목록"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["notification_type", "is_read"]),
        ]

    def __str__(self):
        return f"{self.recipient.nickname}의 {self.get_notification_type_display()} 알림"


class NotificationTemplate(TimeStampedModel):
    """
    알림 템플릿 모델
    각 알림 유형별 메시지 템플릿 관리
    """

    notification_type = models.CharField(
        max_length=20, choices=Notification.NOTIFICATION_TYPES, unique=True
    )
    title_template = models.CharField(
        max_length=100, help_text="제목 템플릿. {변수} 형식으로 변수 지정 가능"
    )
    message_template = models.TextField(help_text="메시지 템플릿. {변수} 형식으로 변수 지정 가능")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "알림 템플릿"
        verbose_name_plural = "알림 템플릿 목록"

    def __str__(self):
        return f"{self.get_notification_type_display()} 알림 템플릿"


class WebPushSubscription(TimeStampedModel):
    """
    웹 푸시 구독 정보 모델
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='push_subscriptions'
    )
    endpoint = models.URLField(max_length=500)
    p256dh = models.CharField(max_length=255)  # Public key
    auth = models.CharField(max_length=255)    # Auth secret
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "웹 푸시 구독"
        verbose_name_plural = "웹 푸시 구독 목록"
        unique_together = ['user', 'endpoint']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['endpoint']),
        ]

    def __str__(self):
        return f"{self.user.nickname}의 웹 푸시 구독"