from common.permissions import IsRequestReceiver
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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


class FriendRequestResponseView(generics.UpdateAPIView):
    """친구 요청 응답"""

    serializer_class = FriendRequestResponseSerializer
    permission_classes = [IsAuthenticated, IsRequestReceiver]
    lookup_url_kwarg = "request_id"

    def get_queryset(self):
        return FriendRelation.objects.filter(
            to_user=self.request.user, status="pending"
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != "pending":
            return Response(
                {"detail": "이미 처리된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)


class FriendListView(generics.ListAPIView):
    """친구 목록 조회"""

    serializer_class = FriendListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        search = self.request.query_params.get("search", "")

        queryset = FriendRelation.objects.filter(
            Q(from_user=user) | Q(to_user=user), status="accepted"
        ).select_related("from_user", "to_user")

        if search:
            queryset = queryset.filter(
                Q(from_user__nickname__icontains=search)
                | Q(to_user__nickname__icontains=search)
            )

        return queryset


class FriendDetailView(generics.RetrieveDestroyAPIView):
    """친구 상세 정보 조회 및 삭제"""

    serializer_class = FriendDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "friend_id"

    def get_queryset(self):
        user = self.request.user
        return FriendRelation.objects.filter(
            Q(from_user=user) | Q(to_user=user), status="accepted"
        )

    def perform_destroy(self, instance):
        if instance.status != "accepted":
            return Response(
                {"detail": "수락된 친구 관계만 삭제할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        instance.status = "rejected"
        instance.save()


class PendingRequestListView(generics.ListAPIView):
    """대기 중인 친구 요청 목록"""

    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRelation.objects.filter(
            to_user=self.request.user, status="pending"
        ).select_related("from_user")


class SentRequestListView(generics.ListAPIView):
    """보낸 친구 요청 목록"""

    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRelation.objects.filter(
            from_user=self.request.user, status="pending"
        ).select_related("to_user")
