from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    """기본 메시지 시리얼라이저"""

    sender_nickname = serializers.CharField(source="sender.nickname", read_only=True)
    receiver_nickname = serializers.CharField(
        source="receiver.nickname", read_only=True
    )
    sender_profile = serializers.SerializerMethodField()
    receiver_profile = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "sender",
            "sender_nickname",
            "sender_profile",
            "receiver",
            "receiver_nickname",
            "receiver_profile",
            "content",
            "is_read",
            "read_at",
            "created_at",
        )
        read_only_fields = ("sender", "is_read", "read_at")

    def get_sender_profile(self, obj):
        return {
            "id": obj.sender.id,
            "profile_image": obj.sender.profile_image.url
            if obj.sender.profile_image
            else None,
        }

    def get_receiver_profile(self, obj):
        return {
            "id": obj.receiver.id,
            "profile_image": obj.receiver.profile_image.url
            if obj.receiver.profile_image
            else None,
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

    other_user = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ("id", "other_user", "preview", "is_read", "created_at")

    def get_other_user(self, obj):
        request = self.context.get("request")
        if not request:
            return None

        user = request.user
        other_user = obj.receiver if obj.sender == user else obj.sender

        return {
            "id": other_user.id,
            "nickname": other_user.nickname,
            "profile_image": other_user.profile_image.url
            if other_user.profile_image
            else None,
        }

    def get_preview(self, obj):
        return obj.content[:30] + "..." if len(obj.content) > 30 else obj.content


class ReceivedMessageSerializer(MessageListSerializer):
    """받은 쪽지함용 시리얼라이저"""

    sender_nickname = serializers.CharField(source="sender.nickname")

    class Meta(MessageListSerializer.Meta):
        fields = MessageListSerializer.Meta.fields + ("sender_nickname",)


class SentMessageSerializer(MessageListSerializer):
    """보낸 쪽지함용 시리얼라이저"""

    receiver_nickname = serializers.CharField(source="receiver.nickname")

    class Meta(MessageListSerializer.Meta):
        fields = MessageListSerializer.Meta.fields + ("receiver_nickname",)


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


class MessageDeleteSerializer(serializers.Serializer):
    """메시지 삭제용 시리얼라이저"""

    message_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)

    def validate_message_ids(self, value):
        user = self.context["request"].user
        messages = Message.objects.filter(id__in=value)

        # 존재하지 않는 메시지 ID 체크
        if len(messages) != len(value):
            raise serializers.ValidationError(_("존재하지 않는 메시지가 포함되어 있습니다."))

        # 권한 체크
        for message in messages:
            if message.sender != user and message.receiver != user:
                raise serializers.ValidationError(_("삭제 권한이 없는 메시지가 포함되어 있습니다."))

            # 이미 삭제된 메시지 체크
            if (user == message.sender and message.deleted_by_sender) or (
                user == message.receiver and message.deleted_by_receiver
            ):
                raise serializers.ValidationError(_("이미 삭제된 메시지가 포함되어 있습니다."))

        return value
