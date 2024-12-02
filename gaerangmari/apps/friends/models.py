from core.models import TimeStampedModel
from django.conf import settings
from django.db import models


class FriendRelation(TimeStampedModel):
    """
    친구 관계
    """

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friend_requests_sent",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friend_requests_received",
    )
    status = models.CharField(
        max_length=20,
        choices=[("pending", "대기중"), ("accepted", "수락됨"), ("rejected", "거절됨")],
        default="pending",
    )

    class Meta:
        verbose_name = "친구 관계"
        verbose_name_plural = "친구 관계 목록"
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"{self.from_user.nickname} -> {self.to_user.nickname}"
