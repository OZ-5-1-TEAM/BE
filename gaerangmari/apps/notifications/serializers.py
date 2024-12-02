from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Notification, NotificationTemplate


class NotificationSerializer(serializers.ModelSerializer):
    """알림 기본 시리얼라이저"""

    sender_profile = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "notification_type",
            "title",
            "message",
            "sender_profile",
            "is_read",
            "read_at",
            "created_at",
            "content_type",
            "object_id",
        )
        read_only_fields = (
            "notification_type",
            "title",
            "message",
            "sender_profile",
            "is_read",
            "read_at",
            "created_at",
        )

    def get_sender_profile(self, obj):
        if obj.sender:
            return {
                "id": obj.sender.id,
                "nickname": obj.sender.nickname,
                "profile_image": obj.sender.profile_image.url
                if obj.sender.profile_image
                else None,
            }
        return None


class NotificationListSerializer(NotificationSerializer):
    """알림 목록 조회용 시리얼라이저"""

    reference_url = serializers.SerializerMethodField()

    class Meta(NotificationSerializer.Meta):
        fields = NotificationSerializer.Meta.fields + ("reference_url",)

    def get_reference_url(self, obj):
        """알림 관련 컨텐츠로 이동할 URL 생성"""
        if obj.content_type and obj.object_id:
            if obj.notification_type == "message":
                return f"/messages/{obj.object_id}"
            elif obj.notification_type in ["comment", "reply", "like"]:
                return f"/posts/{obj.object_id}"
            elif obj.notification_type in ["friend_request", "friend_accept"]:
                return f"/friends/{obj.object_id}"
        return None


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """알림 읽음 처리용 시리얼라이저"""

    class Meta:
        model = Notification
        fields = ("is_read",)
        read_only_fields = ("is_read",)


class NotificationSettingsUpdateSerializer(serializers.Serializer):
    """알림 설정 업데이트용 시리얼라이저"""

    push_enabled = serializers.BooleanField(required=False)
    message_notification = serializers.BooleanField(required=False)
    friend_notification = serializers.BooleanField(required=False)
    comment_notification = serializers.BooleanField(required=False)
    like_notification = serializers.BooleanField(required=False)

    def validate(self, data):
        if not data:
            raise serializers.ValidationError(_("최소한 하나의 설정은 변경되어야 합니다."))
        return data


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """알림 템플릿 시리얼라이저 (관리자용)"""

    class Meta:
        model = NotificationTemplate
        fields = (
            "id",
            "notification_type",
            "title_template",
            "message_template",
            "is_active",
        )

    def validate_title_template(self, value):
        """제목 템플릿 유효성 검사"""
        if not any(marker in value for marker in ["{sender}", "{action}"]):
            raise serializers.ValidationError(
                _("템플릿에는 최소한 {sender}나 {action} 변수가 포함되어야 합니다.")
            )
        return value

    def validate_message_template(self, value):
        """메시지 템플릿 유효성 검사"""
        if not any(marker in value for marker in ["{sender}", "{action}", "{content}"]):
            raise serializers.ValidationError(
                _("템플릿에는 최소한 {sender}, {action}, {content} 변수 중 하나가 포함되어야 합니다.")
            )
        return value


class NotificationBulkDeleteSerializer(serializers.Serializer):
    """알림 대량 삭제용 시리얼라이저"""

    notification_ids = serializers.ListField(
        child=serializers.IntegerField(), min_length=1
    )
    delete_all = serializers.BooleanField(default=False)

    def validate(self, data):
        if data.get("delete_all") and data.get("notification_ids"):
            raise serializers.ValidationError(_("전체 삭제와 선택 삭제는 동시에 수행할 수 없습니다."))

        if not data.get("delete_all") and not data.get("notification_ids"):
            raise serializers.ValidationError(_("삭제할 알림을 선택하거나 전체 삭제를 선택해주세요."))

        return data


class FCMTokenSerializer(serializers.Serializer):
    """FCM 토큰 등록용 시리얼라이저"""

    token = serializers.CharField(max_length=255)
    device_type = serializers.ChoiceField(choices=["ios", "android", "web"])

    def validate_token(self, value):
        if len(value) < 32:
            raise serializers.ValidationError(_("유효하지 않은 FCM 토큰입니다."))
        return value
