# from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Friendship
from users.models import User  # 사용자 모델

# 친구요청 생성, 수락/거절 등 
def send_friend_request(request, user_id):
    addressee = get_object_or_404(User, id=user_id)
    friendship, created = Friendship.objects.get_or_create(
        requester=request.user, addressee=addressee
    )
    if not created:
        return JsonResponse({"error": "Friend request already exists."}, status=400)

    return JsonResponse({"message": "Friend request sent."}, status=200)
