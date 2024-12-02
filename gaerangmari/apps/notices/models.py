from core.models import SoftDeleteModel, TimeStampedModel
from django.conf import settings
from django.db import models


class Notice(SoftDeleteModel):
    """
    공지사항 모델
    """

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # 작성자 삭제 방지
        related_name="notices",
    )
    is_pinned = models.BooleanField(default=False, help_text="상단 고정 여부")
    views = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField(null=True, blank=True, help_text="공지 시작일시")
    end_date = models.DateTimeField(null=True, blank=True, help_text="공지 종료일시")

    class Meta:
        verbose_name = "공지사항"
        verbose_name_plural = "공지사항 목록"
        ordering = ["-is_pinned", "-created_at"]
        indexes = [
            models.Index(fields=["is_pinned", "-created_at"]),
        ]

    def __str__(self):
        return self.title


class NoticeImage(TimeStampedModel):
    """
    공지사항 이미지 모델
    """

    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="notices/%Y/%m/%d/")
    order = models.PositiveSmallIntegerField(default=0, help_text="이미지 순서")

    class Meta:
        verbose_name = "공지사항 이미지"
        verbose_name_plural = "공지사항 이미지 목록"
        ordering = ["notice", "order"]

    def __str__(self):
        return f"{self.notice.title}의 이미지 {self.order}"


class NoticeFile(TimeStampedModel):
    """
    공지사항 첨부파일 모델
    """

    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(
        upload_to="notices/files/%Y/%m/%d/", help_text="첨부파일 (최대 10MB)"
    )
    filename = models.CharField(max_length=255, help_text="원본 파일명")
    file_size = models.PositiveIntegerField(help_text="파일 크기 (bytes)")
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "공지사항 첨부파일"
        verbose_name_plural = "공지사항 첨부파일 목록"
        ordering = ["notice", "created_at"]

    def __str__(self):
        return f"{self.notice.title}의 첨부파일 {self.filename}"


class NoticeRead(TimeStampedModel):
    """
    공지사항 읽음 여부 모델
    """

    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name="reads")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notice_reads"
    )

    class Meta:
        verbose_name = "공지사항 읽음"
        verbose_name_plural = "공지사항 읽음 목록"
        unique_together = ("notice", "user")
        indexes = [
            models.Index(fields=["user", "notice"]),
        ]

    def __str__(self):
        return f"{self.user.nickname}의 {self.notice.title} 읽음"
