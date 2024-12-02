from django.db import models


class TimeStampedModel(models.Model):
    """
    생성일시, 수정일시를 자동으로 기록하는 추상 기본 모델
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    """
    소프트 삭제를 지원하는 추상 모델
    """

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
