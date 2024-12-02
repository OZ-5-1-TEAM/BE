from core.models import SoftDeleteModel, TimeStampedModel
from django.conf import settings
from django.db import models


class Pet(SoftDeleteModel):
    """
    반려동물 모델
    """

    name = models.CharField(max_length=50)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pets"
    )
    breed = models.CharField(max_length=50)
    age = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    size = models.CharField(
        max_length=10, choices=[("small", "소형"), ("medium", "중형"), ("large", "대형")]
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="pets/%Y/%m/%d/", null=True, blank=True)

    class Meta:
        verbose_name = "반려동물"
        verbose_name_plural = "반려동물 목록"

    def __str__(self):
        return f"{self.owner.nickname}의 {self.name}"
