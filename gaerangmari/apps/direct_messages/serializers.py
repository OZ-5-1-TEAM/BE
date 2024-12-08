from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    """기본 메시지 시리얼라이저"""
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "sender",
            "receiver",
            "content",
            "is_read",
            "read_at",
            "created_at",
        )
        read_only_fields = ("sender", "is_read", "read_at")

    def get_sender(self, obj):
        return {
            "id": obj.sender.id,
            "nickname": obj.sender.nickname,
            "profile_image": obj.sender.profile_image.url if obj.sender.profile_image else None,
        }

    def get_receiver(self, obj):
        return {
            "id": obj.receiver.id,
            "nickname": obj.receiver.nickname,
            "profile_image": obj.receiver.profile_image.url if obj.receiver.profile_image else None,
        }


class MessageCreateSerializer(serializers.ModelSerializer):
    """메시지 작성용 시리얼라이저"""

    class Meta:
        model = Message
        fields = ("receiver", "content")

    def validate_content(self, value):
        if len(value) > 500:
            raise serializers.ValidationError(_("메시지는 500자를 초과할 수 없습니다."))
        return value

    def validate_receiver(self, value):
        user = self.context["request"].user
        if value == user:
            raise serializers.ValidationError(_("자기 자신에게 쪽지를 보낼 수 없습니다."))
        return value

    def create(self, validated_data):
        validated_data["sender"] = self.context["request"].user
        return super().create(validated_data)


class MessageListSerializer(serializers.ModelSerializer):
    """메시지 목록 조회용 시리얼라이저"""
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ("id", "sender", "receiver", "preview", "content", "is_read", "created_at")

    def get_sender(self, obj):
        return {
            "nickname": obj.sender.nickname
        }

    def get_receiver(self, obj):
        return {
            "nickname": obj.receiver.nickname
        }

    def get_preview(self, obj):
        return obj.content[:30] + "..." if len(obj.content) > 30 else obj.content


class ReceivedMessageSerializer(MessageListSerializer):
    """받은 쪽지함용 시리얼라이저"""

    class Meta(MessageListSerializer.Meta):
        fields = ("id", "sender", "content", "is_read", "created_at")


class SentMessageSerializer(MessageListSerializer):
    """보낸 쪽지함용 시리얼라이저"""

    class Meta(MessageListSerializer.Meta):
        fields = ("id", "receiver", "content", "is_read", "created_at")


class MessageDetailSerializer(MessageSerializer):
    """메시지 상세 조회용 시리얼라이저"""

    class Meta(MessageSerializer.Meta):
        fields = MessageSerializer.Meta.fields + (
            "deleted_by_sender",
            "deleted_by_receiver",
        )

    def to_representation(self, instance):
        """
        요청한 사용자가 삭제한 메시지는 표시하지 않음
        """
        request = self.context.get("request")
        if not request:
            return super().to_representation(instance)

        user = request.user
        if (user == instance.sender and instance.deleted_by_sender) or (
            user == instance.receiver and instance.deleted_by_receiver
        ):
            return None

        return super().to_representation(instance)