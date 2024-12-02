from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Pet


class PetSerializer(serializers.ModelSerializer):
    """
    반려동물 시리얼라이저
    기본적인 CRUD 작업에 사용
    """

    owner_nickname = serializers.CharField(source="owner.nickname", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = (
            "id",
            "name",
            "owner",
            "owner_nickname",
            "breed",
            "age",
            "weight",
            "size",
            "description",
            "image",
            "image_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("owner", "created_at", "updated_at")
        extra_kwargs = {"image": {"write_only": True}}

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def validate_weight(self, value):
        """
        무게 유효성 검사
        """
        if value and value <= 0:
            raise serializers.ValidationError(_("무게는 0보다 커야 합니다."))
        return value

    def validate_age(self, value):
        """
        나이 유효성 검사
        """
        if value and value < 0:
            raise serializers.ValidationError(_("나이는 0보다 작을 수 없습니다."))
        return value

    def create(self, validated_data):
        """
        현재 로그인한 사용자를 owner로 지정
        """
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class PetListSerializer(serializers.ModelSerializer):
    """
    반려동물 목록 조회용 시리얼라이저
    """

    owner_nickname = serializers.CharField(source="owner.nickname", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = (
            "id",
            "name",
            "owner_nickname",
            "breed",
            "size",
            "image_url",
            "created_at",
        )

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class PetDetailSerializer(PetSerializer):
    """
    반려동물 상세 정보 시리얼라이저
    기본 시리얼라이저를 상속받아 추가 정보 포함
    """

    owner_profile = serializers.SerializerMethodField()

    class Meta(PetSerializer.Meta):
        fields = PetSerializer.Meta.fields + ("owner_profile",)

    def get_owner_profile(self, obj):
        return {
            "id": obj.owner.id,
            "nickname": obj.owner.nickname,
            "profile_image": obj.owner.profile_image.url
            if obj.owner.profile_image
            else None,
            "district": obj.owner.district,
            "neighborhood": obj.owner.neighborhood,
        }


class PetCreateSerializer(PetSerializer):
    """
    반려동물 생성 전용 시리얼라이저
    """

    class Meta(PetSerializer.Meta):
        fields = ("name", "breed", "age", "weight", "size", "description", "image")

    def validate(self, data):
        """
        반려동물 등록 개수 제한 검사
        """
        user = self.context["request"].user
        if Pet.objects.filter(owner=user, is_deleted=False).count() >= 5:
            raise serializers.ValidationError(_("반려동물은 최대 5마리까지만 등록할 수 있습니다."))
        return data


class PetUpdateSerializer(PetSerializer):
    """
    반려동물 정보 수정 전용 시리얼라이저
    """

    class Meta(PetSerializer.Meta):
        fields = ("name", "breed", "age", "weight", "size", "description", "image")
        extra_kwargs = {
            "name": {"required": False},
            "breed": {"required": False},
            "size": {"required": False},
        }

    def validate(self, data):
        """
        최소한 하나의 필드는 수정되어야 함
        """
        if not data:
            raise serializers.ValidationError(_("수정할 정보를 입력해주세요."))
        return data
