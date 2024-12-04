from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """회원가입 시리얼라이저"""

    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "password_confirm", "nickname")

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})

        try:
            validate_password(data["password"])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["email"], **validated_data
        )
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """사용자 프로필 시리얼라이저"""

    class Meta:
        model = UserProfile
        fields = ("bio",)


class UserDetailSerializer(serializers.ModelSerializer):
    """사용자 상세정보 시리얼라이저"""

    profile = UserProfileSerializer(required=False)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nickname",
            "profile_image",
            "district",
            "neighborhood",
            "profile",
            "push_enabled",
            "message_notification",
            "friend_notification",
            "comment_notification",
            "like_notification",
        )
        read_only_fields = ("email",)

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data and instance.profile:
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            instance.profile.save()

        return instance


class SocialLoginSerializer(serializers.Serializer):
    """소셜 로그인 시리얼라이저"""

    provider = serializers.ChoiceField(choices=["kakao", "google"])
    access_token = serializers.CharField()


class PasswordChangeSerializer(serializers.Serializer):
    """비밀번호 변경 시리얼라이저"""

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError({"new_password": "새 비밀번호가 일치하지 않습니다."})

        try:
            validate_password(data["new_password"])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})

        return data

class EmailVerificationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField()

class PasswordResetSerializer(serializers.Serializer):
    """비밀번호 재설정 시리얼라이저"""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("등록되지 않은 이메일입니다.")
        return value



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserDetailSerializer(self.user).data
        return data