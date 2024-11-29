from django.db import models
from django.conf import settings

class Friendship(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), #요청대기
        ('accepted', 'Accepted'), #친구수락
        ('rejected', 'Rejected'), #친구거절
    ]

# 친구요청을 보낸 사용자
    requester = models.ForeignKey(  
        settings.AUTH_USER_MODEL, 
        related_name='friend_requests_sent', #사용자가 보낸 모든 요청 조회 
        on_delete=models.CASCADE #사용자가 삭제되면 연결된 친구요청도 삭제
    )

# 친구 요청을 받은 사용자
    addressee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='friend_requests_received', 
        on_delete=models.CASCADE
    )

# 친구 요청의 상태를 저장
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending' 
    )
    created_at = models.DateTimeField(auto_now_add=True) #객체가 처음 생성된 시간을 자동으로 기록
    updated_at = models.DateTimeField(auto_now=True) #객체가 마지막으로 수정된 시간을 자동으로 기록

    class Meta:
        unique_together = ('requester', 'addressee')  # 중복요청 방지
        ordering = ['-created_at'] # created_at 기준 내림차순으로 설정 / 최신요청이 먼저 나타남

    def __str__(self):
        return f"{self.requester} -> {self.addressee} ({self.status})"
