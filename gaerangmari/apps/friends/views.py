from common.permissions import IsRequestReceiver
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from common.pagination import StandardResultsSetPagination
from common.response import CustomResponse
from .models import FriendRelation
from .serializers import (
    FriendDetailSerializer,
    FriendListSerializer,
    FriendRequestResponseSerializer,
    FriendRequestSerializer,
)


class FriendRequestCreateView(generics.CreateAPIView):
    """친구 요청 보내기"""

    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

# FriendRequestResponseView 수정
class FriendRequestResponseView(generics.UpdateAPIView):
    """친구 요청 응답 및 삭제"""
    serializer_class = FriendRequestResponseSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "friend_id"  # request_id에서 friend_id로 변경

    def get_queryset(self):
        return FriendRelation.objects.filter(
            Q(to_user=self.request.user) | Q(from_user=self.request.user)
        ).order_by('-created_at')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        status_value = request.data.get('status')
        
        # 친구 요청 처리
        if instance.status == "pending" and status_value in ['accepted', 'rejected']:
            if instance.to_user != request.user:
                return Response(
                    {"detail": "친구 요청을 처리할 권한이 없습니다."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            return super().update(request, *args, **kwargs)
            
        # 친구 삭제 처리
        elif instance.status == "accepted" and status_value == 'rejected':
            instance.status = 'rejected'
            instance.save()
            return Response({"detail": "친구 삭제 완료"}, status=status.HTTP_200_OK)
            
        return Response(
            {"detail": "잘못된 요청입니다."}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class FriendListView(generics.ListAPIView):
    """친구 목록 조회"""
    pagination_class = StandardResultsSetPagination
    serializer_class = FriendListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        search = self.request.query_params.get("search", "")

        queryset = FriendRelation.objects.filter(
            Q(from_user=user) | Q(to_user=user), status="accepted"
        ).select_related("from_user", "to_user").order_by('-created_at')

        if search:
            queryset = queryset.filter(
                Q(from_user__nickname__icontains=search)
                | Q(to_user__nickname__icontains=search)
            ).order_by('-created_at')

        return queryset




class PendingRequestListView(generics.ListAPIView):
    """대기 중인 친구 요청 목록"""

    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRelation.objects.filter(
            to_user=self.request.user, status="pending"
        ).select_related("from_user").order_by('-created_at')


class SentRequestListView(generics.ListAPIView):
    """보낸 친구 요청 목록"""

    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRelation.objects.filter(
            from_user=self.request.user, 
            status="pending"
        ).select_related("to_user").order_by('-created_at')