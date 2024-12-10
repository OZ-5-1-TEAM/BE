from core.models import SoftDeleteModel, TimeStampedModel
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError


class Post(SoftDeleteModel):
    """
    게시글 모델
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    category = models.CharField(
        max_length=20,
        choices=[
            ("notice", "공지사항"),
            ("dog", "강아지 커뮤니티"),
            ("mate", "산책메이트 커뮤니티"),
        ],
    )
    district = models.CharField(max_length=20)  # 구
    neighborhood = models.CharField(max_length=20)  # 동
    dog_size = models.CharField(
        max_length=10,
        choices=[("small", "소형"), ("medium", "중형"), ("large", "대형")],
        null=True,
        blank=True,
    )
    views = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    comments_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "게시글"
        verbose_name_plural = "게시글 목록"
        ordering = ['-created_at']  # 기본 정렬 순서 추가
        indexes = [
            models.Index(fields=["category", "-created_at"]),
            models.Index(fields=["district", "neighborhood"]),
        ]

    def __str__(self):
        return self.title


class PostImage(TimeStampedModel):
    """
    게시글 이미지 모델
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="posts/%Y/%m/%d/")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "게시글 이미지"
        verbose_name_plural = "게시글 이미지 목록"
        ordering = ["order"]


class Comment(SoftDeleteModel):
    """
    댓글 모델
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    content = models.TextField()
    level = models.PositiveSmallIntegerField(default=0)  # 댓글 depth 레벨 추가

    class Meta:
        verbose_name = "댓글"
        verbose_name_plural = "댓글 목록"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.nickname}의 댓글"

    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.content = "삭제된 댓글입니다."  # soft delete 시 기본 메시지 설정
        self.is_deleted = True
        self.save()


class Like(TimeStampedModel):
    """
    좋아요 모델
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        verbose_name = "좋아요"
        verbose_name_plural = "좋아요 목록"
        unique_together = ("post", "user")


class Report(TimeStampedModel):
    """
    신고 모델
    """
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_sent"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="reports", null=True, blank=True
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="reports", null=True, blank=True
    )
    reason = models.CharField(
        max_length=50,
        choices=[
            ("spam", "스팸"),
            ("abuse", "욕설/비방"),
            ("adult", "성인성 콘텐츠"),
            ("privacy", "개인정보 노출"),
            ("etc", "기타"),
        ],
    )
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[("pending", "대기"), ("accepted", "승인"), ("rejected", "거절")],
        default="pending",
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_reports",
    )

    class Meta:
        verbose_name = "신고"
        verbose_name_plural = "신고 목록"

    def clean(self):
        # post와 comment 중 하나만 설정되어야 함을 검증
        if not self.post and not self.comment:
            raise ValidationError("게시글이나 댓글 중 하나는 반드시 지정되어야 합니다.")
        if self.post and self.comment:
            raise ValidationError("게시글과 댓글 중 하나만 지정할 수 있습니다.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)