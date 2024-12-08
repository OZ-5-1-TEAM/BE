from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    """회원가입 시리얼라이저"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)  # password_confirm → confirm_password
    district = serializers.CharField(required=True)
    neighborhood = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "confirm_password",
            "nickname",
            "district",
            "neighborhood"
        )
        
    def validate(self, data):
        # 비밀번호 확인 검증
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "password": "비밀번호가 일치하지 않습니다."
            })
        
        # 닉네임 길이 검증 (2~10자)
        if len(data["nickname"]) < 2 or len(data["nickname"]) > 10:
            raise serializers.ValidationError({
                "nickname": "닉네임은 2~10자 사이여야 합니다."
            })

        try:
            validate_password(data["password"])
        except ValidationError as e:
            raise serializers.ValidationError({
                "password": e.messages
            })

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")  # password_confirm → confirm_password
        user = User.objects.create_user(
            username=validated_data["email"],
            **validated_data
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
    profilePhoto = serializers.ImageField(source='profile_image', required=False)
    additionalPhoto = serializers.ImageField(required=False)
    bio = serializers.CharField(required=False, allow_blank=True)
    intro = serializers.CharField(source='bio', required=False)  # API 명세의 intro와 기존 bio 필드 매핑
    
    class Meta:
        model = User
        fields = (
            'email',
            'nickname',
            'profilePhoto',
            'additionalPhoto',
            'district',
            'neighborhood',
            'bio',
            'intro'
        )
        read_only_fields = ('email',)

    def validate(self, data):
        # 파일 검증
        profile_photo = self.context['request'].FILES.get('profilePhoto')
        additional_photo = self.context['request'].FILES.get('additionalPhoto')
        
        for photo in [profile_photo, additional_photo]:
            if photo:
                # 파일 크기 검증 (5MB)
                if photo.size > 5 * 1024 * 1024:
                    raise serializers.ValidationError({
                        "error": "INVALID_FILE",
                        "message": "파일 크기는 5MB 이하이어야 합니다."
                    })
                
                # 파일 형식 검증 (JPEG, PNG)
                if not photo.content_type in ['image/jpeg', 'image/png']:
                    raise serializers.ValidationError({
                        "error": "INVALID_FILE",
                        "message": "파일 형식은 JPEG 또는 PNG여야 합니다."
                    })
        
        return data

    def to_representation(self, instance):
        """API 응답 형식에 맞게 데이터 변환"""
        ret = super().to_representation(instance)
        
        # profile 관련 데이터 처리
        if hasattr(instance, 'profile') and instance.profile:
            ret['bio'] = instance.profile.bio
        
        # 불필요한 필드 제거
        if 'intro' in ret:
            ret.pop('intro')  # intro는 내부적으로만 사용하고 응답에서는 bio로 통일
            
        return ret

    def update(self, instance, validated_data):
        """프로필 업데이트 처리"""
        # 이미지 필드 처리
        profile_image = validated_data.pop('profile_image', None)
        if profile_image:
            instance.profile_image = profile_image
            
        additional_photo = validated_data.pop('additional_photo', None)
        if additional_photo:
            instance.additional_image = additional_photo
            
        # bio/intro 처리
        bio = validated_data.pop('bio', None)
        if bio and instance.profile:
            instance.profile.bio = bio
            instance.profile.save()
            
        # 나머지 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """비밀번호 변경 시리얼라이저"""
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "새 비밀번호가 일치하지 않습니다."
            })

        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                "new_password": e.messages
            })

        return data

class SocialLoginSerializer(serializers.Serializer):
    """소셜 로그인 시리얼라이저"""
    provider = serializers.ChoiceField(choices=['kakao', 'google'])
    access_token = serializers.CharField(required=True)

    def validate_provider(self, value):
        if value not in ['kakao', 'google']:
            raise serializers.ValidationError(
                "지원하지 않는 소셜 로그인입니다."
            )
        return value


class PasswordResetSerializer(serializers.Serializer):
    """비밀번호 재설정 시리얼라이저"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("등록되지 않은 이메일입니다.")
        return value


class EmailVerificationSerializer(serializers.Serializer):
    """이메일 인증 시리얼라이저"""
    user_id = serializers.IntegerField(required=True)
    code = serializers.CharField(required=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """커스텀 토큰 시리얼라이저"""
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserDetailSerializer(self.user).data
        return data