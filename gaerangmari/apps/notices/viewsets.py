from django.db.models import F
from django.http import FileResponse
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Notice, NoticeFile, NoticeRead
from .serializers import (
    NoticeCreateSerializer,
    NoticeDetailSerializer,
    NoticeListSerializer,
    NoticeUpdateSerializer,
)


class NoticeViewSet(viewsets.ModelViewSet):
    """공지사항 관리를 위한 ViewSet"""

    lookup_url_kwarg = "notice_id"

    def get_queryset(self):
        queryset = Notice.objects.filter(is_deleted=False)

        if self.action == "list":
            # 상단 고정 공지와 일반 공지 분리하여 정렬
            queryset = queryset.order_by("-is_pinned", "-created_at")

            # 검색 기능
            search = self.request.query_params.get("search")
            if search:
                queryset = queryset.filter(title__icontains=search) | queryset.filter(
                    content__icontains=search
                )

        return queryset

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == "list":
            return NoticeListSerializer
        elif self.action == "retrieve":
            return NoticeDetailSerializer
        elif self.action == "create":
            return NoticeCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return NoticeUpdateSerializer
        return NoticeDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # 조회수 증가
        instance.views = F("views") + 1
        instance.save()
        instance.refresh_from_db()

        # 읽음 처리
        if request.user.is_authenticated:
            NoticeRead.objects.get_or_create(notice=instance, user=request.user)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="files/(?P<file_id>[^/.]+)")
    def download_file(self, request, notice_id=None, file_id=None):
        """첨부파일 다운로드"""
        notice_file = generics.get_object_or_404(
            NoticeFile, id=file_id, notice_id=notice_id, notice__is_deleted=False
        )

        # 다운로드 카운트 증가
        notice_file.download_count = F("download_count") + 1
        notice_file.save()

        response = FileResponse(notice_file.file)
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{notice_file.filename}"'
        return response

    @action(detail=True, methods=["post"])
    def pin(self, request, notice_id=None):
        """공지사항 상단 고정/해제"""
        notice = self.get_object()
        notice.is_pinned = not notice.is_pinned
        notice.save()
        return Response(
            {
                "is_pinned": notice.is_pinned,
                "message": "공지사항이 상단에 고정되었습니다."
                if notice.is_pinned
                else "공지사항 상단 고정이 해제되었습니다.",
            }
        )
