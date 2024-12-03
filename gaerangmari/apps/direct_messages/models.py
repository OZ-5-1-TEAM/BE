from django.utils import timezone

from core.models import SoftDeleteModel, TimeStampedModel
from django.conf import settings
from django.db import models


class Message(SoftDeleteModel):
    """
    쪽지 모델
    """

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    content = models.TextField(max_length=500)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_receiver = models.BooleanField(default=False)

    class Meta:
        verbose_name = "쪽지"
        verbose_name_plural = "쪽지 목록"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sender", "-created_at"]),
            models.Index(fields=["receiver", "-created_at"]),
        ]

    def __str__(self):
        return f"From {self.sender.nickname} to {self.receiver.nickname}"

    def soft_delete(self, user):
        """
        발신자/수신자별 쪽지 삭제 처리
        """
        if user == self.sender:
            self.deleted_by_sender = True
        elif user == self.receiver:
            self.deleted_by_receiver = True

        if self.deleted_by_sender and self.deleted_by_receiver:
            self.is_deleted = True
            self.deleted_at = timezone.now()

        self.save()
