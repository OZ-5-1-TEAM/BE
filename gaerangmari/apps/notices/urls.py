from django.urls import path

from . import views

app_name = "notices"

urlpatterns = [
    path("", views.NoticeListView.as_view(), name="notice-list"),
    path("create/", views.NoticeCreateView.as_view(), name="notice-create"),
    path("<int:notice_id>/", views.NoticeDetailView.as_view(), name="notice-detail"),
    path(
        "<int:notice_id>/update/",
        views.NoticeUpdateView.as_view(),
        name="notice-update",
    ),
    path(
        "<int:notice_id>/delete/",
        views.NoticeDeleteView.as_view(),
        name="notice-delete",
    ),
    path(
        "<int:notice_id>/files/<int:file_id>/",
        views.NoticeFileDownloadView.as_view(),
        name="notice-file-download",
    ),
]

# 공지사항 목록 조회 (GET /api/v1/notices)
# 공지사항 작성 (POST /api/v1/notices)
# 공지사항 상세 조회 (GET /api/v1/notices/{notice_id})
# 공지사항 수정 (PUT /api/v1/notices/{notice_id})
# 공지사항 삭제 (DELETE /api/v1/notices/{notice_id})
# 공지사항 첨부파일 다운로드 (GET /api/v1/notices/{notice_id}/files/{file_id})
