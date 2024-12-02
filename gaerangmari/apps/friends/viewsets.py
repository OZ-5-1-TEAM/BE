from common.permissions import IsRequestReceiver
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
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


class FriendViewSet(viewsets.ModelViewSet):
    """친구 관계 관리 ViewSet"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        search = self.request.query_params.get("search", "")

        queryset = FriendRelation.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        ).select_related("from_user", "to_user")

        if search:
            queryset = queryset.filter(
                Q(from_user__nickname__icontains=search)
                | Q(to_user__nickname__icontains=search)
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return FriendRequestSerializer
        elif self.action == "respond":
            return FriendRequestResponseSerializer
        elif self.action == "retrieve":
            return FriendDetailSerializer
        return FriendListSerializer

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    @action(detail=True, methods=["put"])
    def respond(self, request, pk=None):
        """친구 요청 응답"""
        instance = self.get_object()

        if instance.to_user != request.user:
            return Response(
                {"detail": "이 요청에 대한 응답 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        if instance.status != "pending":
            return Response(
                {"detail": "이미 처리된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """대기 중인 친구 요청 목록"""
        queryset = self.get_queryset().filter(to_user=request.user, status="pending")

        serializer = FriendRequestSerializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, instance):
        """친구 관계 삭제"""
        if instance.status != "accepted":
            return Response(
                {"detail": "수락된 친구 관계만 삭제할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = "rejected"
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
