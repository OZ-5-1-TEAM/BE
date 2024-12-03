from core.models import TimeStampedModel
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.core.validators import MaxLengthValidator
from django.db import models


class User(AbstractUser):
    """
    사용자 모델
    """
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    email = models.EmailField(unique=True)
    nickname = models.CharField(
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(2)],
        help_text="2~10자의 닉네임을 입력하세요.",
    )
    profile_image = models.ImageField(
        upload_to="profiles/%Y/%m/%d/", null=True, blank=True
    )
    district = models.CharField(max_length=20, null=True, blank=True)  # 구
    neighborhood = models.CharField(max_length=20, null=True, blank=True)  # 동
    status = models.CharField(
        max_length=20,
        choices=[("active", "활성"), ("inactive", "비활성"), ("suspended", "정지")],
        default="active",
    )
    status_changed_at = models.DateTimeField(null=True, blank=True)
    status_reason = models.TextField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    # 소셜 로그인 관련 필드
    is_social = models.BooleanField(default=False)
    social_provider = models.CharField(
        max_length=20,
        choices=[("kakao", "카카오"), ("google", "구글")],
        null=True,
        blank=True,
    )
    social_id = models.CharField(max_length=100, null=True, blank=True)

    # 알림 설정
    push_enabled = models.BooleanField(default=True)
    message_notification = models.BooleanField(default=True)
    friend_notification = models.BooleanField(default=True)
    comment_notification = models.BooleanField(default=True)
    like_notification = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "nickname"]

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자 목록"
        permissions = [
            ("can_view_profile", "Can view profile"),
        ]

    def __str__(self):
        return self.nickname


class UserProfile(TimeStampedModel):
    """
    사용자 프로필 추가 정보
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(
        max_length=500, blank=True, help_text="자기소개를 500자 이내로 작성하세요.",
        validators=[MaxLengthValidator(500)]
    )

    class Meta:
        verbose_name = "사용자 프로필"
        verbose_name_plural = "사용자 프로필 목록"

    def __str__(self):
        return f"{self.user.nickname}의 프로필"