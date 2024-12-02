from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import FriendRelation


class FriendRequestSerializer(serializers.ModelSerializer):
    """친구 요청 시리얼라이저"""

    from_user_nickname = serializers.CharField(
        source="from_user.nickname", read_only=True
    )
    from_user_profile = serializers.SerializerMethodField()
    to_user_nickname = serializers.CharField(source="to_user.nickname", read_only=True)
    to_user_profile = serializers.SerializerMethodField()

    class Meta:
        model = FriendRelation
        fields = (
            "id",
            "from_user",
            "from_user_nickname",
            "from_user_profile",
            "to_user",
            "to_user_nickname",
            "to_user_profile",
            "status",
            "created_at",
        )
        read_only_fields = ("from_user", "status")

    def get_from_user_profile(self, obj):
        return {
            "id": obj.from_user.id,
            "profile_image": obj.from_user.profile_image.url
            if obj.from_user.profile_image
            else None,
            "district": obj.from_user.district,
            "neighborhood": obj.from_user.neighborhood,
        }

    def get_to_user_profile(self, obj):
        return {
            "id": obj.to_user.id,
            "profile_image": obj.to_user.profile_image.url
            if obj.to_user.profile_image
            else None,
            "district": obj.to_user.district,
            "neighborhood": obj.to_user.neighborhood,
        }

    def validate_to_user(self, value):
        user = self.context["request"].user

        if value == user:
            raise serializers.ValidationError(_("자기 자신에게 친구 요청을 보낼 수 없습니다."))

        # 이미 친구 관계인지 확인
        if FriendRelation.objects.filter(
            (
                models.Q(from_user=user, to_user=value)
                | models.Q(from_user=value, to_user=user)
            ),
            status="accepted",
        ).exists():
            raise serializers.ValidationError(_("이미 친구 관계입니다."))

        # 이미 요청을 보냈는지 확인
        if FriendRelation.objects.filter(
            from_user=user, to_user=value, status="pending"
        ).exists():
            raise serializers.ValidationError(_("이미 친구 요청을 보냈습니다."))

        return value

    def create(self, validated_data):
        validated_data["from_user"] = self.context["request"].user
        return super().create(validated_data)


class FriendRequestResponseSerializer(serializers.ModelSerializer):
    """친구 요청 응답 시리얼라이저"""

    class Meta:
        model = FriendRelation
        fields = ("status",)

    def validate_status(self, value):
        if value not in ["accepted", "rejected"]:
            raise serializers.ValidationError(_("올바르지 않은 응답입니다."))
        return value

    def validate(self, data):
        instance = self.instance
        user = self.context["request"].user

        if instance.to_user != user:
            raise serializers.ValidationError(_("이 요청에 대한 응답 권한이 없습니다."))

        if instance.status != "pending":
            raise serializers.ValidationError(_("이미 처리된 요청입니다."))

        return data


class FriendListSerializer(serializers.ModelSerializer):
    """친구 목록 조회용 시리얼라이저"""

    friend = serializers.SerializerMethodField()

    class Meta:
        model = FriendRelation
        fields = ("id", "friend", "created_at")

    def get_friend(self, obj):
        user = self.context["request"].user
        friend = obj.to_user if obj.from_user == user else obj.from_user

        return {
            "id": friend.id,
            "nickname": friend.nickname,
            "profile_image": friend.profile_image.url if friend.profile_image else None,
            "district": friend.district,
            "neighborhood": friend.neighborhood,
        }


class FriendDetailSerializer(FriendListSerializer):
    """친구 상세 정보 시리얼라이저"""

    def get_friend(self, obj):
        friend_info = super().get_friend(obj)
        friend = (
            obj.to_user
            if obj.from_user == self.context["request"].user
            else obj.from_user
        )

        # 추가 정보
        pets = friend.pets.filter(is_deleted=False)
        friend_info.update(
            {
                "pets": [
                    {
                        "id": pet.id,
                        "name": pet.name,
                        "breed": pet.breed,
                        "size": pet.size,
                        "image_url": pet.image.url if pet.image else None,
                    }
                    for pet in pets
                ]
            }
        )

        return friend_info
