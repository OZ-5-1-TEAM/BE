from common.permissions import IsOwner
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from .models import Pet
from .serializers import (
    PetCreateSerializer,
    PetDetailSerializer,
    PetListSerializer,
    PetSerializer,
    PetUpdateSerializer,
)


class PetViewSet(viewsets.ModelViewSet):
    """
    반려동물 관리를 위한 ViewSet
    """

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    lookup_url_kwarg = "pet_id"

    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user, is_deleted=False).order_by(
            "-created_at"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PetListSerializer
        elif self.action == "retrieve":
            return PetDetailSerializer
        elif self.action == "create":
            return PetCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return PetUpdateSerializer
        return PetSerializer

    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """생성 시 현재 사용자를 owner로 지정"""
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        """소프트 삭제 구현"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

    def get_success_headers(self, data):
        """업로드된 이미지를 처리하기 위한 헤더 설정"""
        try:
            return {"Location": str(data["image"])}
        except (TypeError, KeyError):
            return {}

    def list(self, request, *args, **kwargs):
        """목록 조회 시 필터링 및 정렬 적용"""
        queryset = self.get_queryset()

        # 크기별 필터링
        size = request.query_params.get("size")
        if size:
            queryset = queryset.filter(size=size)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """수정 시 부분 수정 허용"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
