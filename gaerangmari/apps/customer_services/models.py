from django.db import models

class CustomerInquiry(models.Model):
    STATUS_CHOICES = (
        ('submitted', '접수됨'),
        ('in_progress', '처리중'),
        ('completed', '처리완료'),
    )

    title = models.CharField(max_length=200)
    email = models.EmailField()
    district = models.CharField(max_length=50)
    neighborhood = models.CharField(max_length=50)
    content = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.email}"