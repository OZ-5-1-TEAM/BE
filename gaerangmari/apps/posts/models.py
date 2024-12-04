from core.models import SoftDeleteModel, TimeStampedModel
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


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
            ("walk", "산책"),
            ("care", "돌봄"),
            ("community", "자유게시판"),         #게시판 종류는 나중에 한번 더확인
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

    class Meta:
        verbose_name = "댓글"
        verbose_name_plural = "댓글 목록"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.nickname}의 댓글"


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
