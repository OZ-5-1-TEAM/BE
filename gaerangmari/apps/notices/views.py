from django.db.models import F
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from common.pagination import StandardResultsSetPagination
from common.response import CustomResponse
from .models import Notice, NoticeRead
from .serializers import (
    NoticeCreateSerializer,
    NoticeDetailSerializer,
    NoticeListSerializer,
    NoticeUpdateSerializer,
)


class NoticeListView(generics.ListAPIView):
    """공지사항 목록 조회"""

    pagination_class = StandardResultsSetPagination
    serializer_class = NoticeListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Notice.objects.filter(is_deleted=False)

        # 상단 고정 공지와 일반 공지 분리하여 정렬
        queryset = queryset.order_by("-is_pinned", "-created_at")

        # 검색 기능
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(
                content__icontains=search
            )

        return queryset


class NoticeDetailView(generics.RetrieveAPIView):
    """공지사항 상세 조회"""

    serializer_class = NoticeDetailSerializer
    permission_classes = [AllowAny]
    lookup_url_kwarg = "notice_id"

    def get_queryset(self):
        return Notice.objects.filter(is_deleted=False)

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


class NoticeCreateView(generics.CreateAPIView):
    """공지사항 작성 (관리자 전용)"""

    serializer_class = NoticeCreateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class NoticeUpdateView(generics.UpdateAPIView):
    """공지사항 수정 (관리자 전용)"""

    serializer_class = NoticeUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_url_kwarg = "notice_id"

    def get_queryset(self):
        return Notice.objects.filter(is_deleted=False)


class NoticeDeleteView(generics.DestroyAPIView):
    """공지사항 삭제 (관리자 전용)"""

    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_url_kwarg = "notice_id"

    def get_queryset(self):
        return Notice.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()


class NoticeFileDownloadView(APIView):
    """공지사항 첨부파일 다운로드"""

    permission_classes = [AllowAny]

    def get(self, request, notice_id, file_id):
        from django.http import FileResponse

        from .models import NoticeFile

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
