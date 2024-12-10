from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Pet(models.Model):
    GENDER_CHOICES = (
        ('M', '수컷'),
        ('F', '암컷'),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pets'
    )
    name = models.CharField(max_length=50)
    breed = models.CharField(max_length=50)
    age = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    size = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    gender = models.CharField(  # 새로 추가된 필드
        max_length=1,
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to='pets/', null=True, blank=True)
    additional_image = models.ImageField(upload_to='pets/', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.owner.nickname}의 {self.name}"