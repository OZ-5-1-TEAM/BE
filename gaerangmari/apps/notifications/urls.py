from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification-list"),
    path(
        "<int:notification_id>/read/",
        views.NotificationMarkReadView.as_view(),
        name="notification-read",
    ),
    path(
        "read-all/",
        views.NotificationMarkReadView.as_view(),
        name="notification-read-all",
    ),
    path(
        "delete/",
        views.NotificationBulkDeleteView.as_view(),
        name="notification-bulk-delete",
    ),
    path(
        "settings/",
        views.NotificationSettingsUpdateView.as_view(),
        name="notification-settings",
    ),
    path("fcm-token/", views.FCMTokenUpdateView.as_view(), name="fcm-token-update"),
]

# 알림 목록 조회 (GET /api/v1/notifications)
# 단일 알림 읽음 처리 (POST /api/v1/notifications/{notification_id}/read)
# 전체 알림 읽음 처리 (POST /api/v1/notifications/read-all)
# 알림 대량 삭제 (POST /api/v1/notifications/delete)
# 알림 설정 업데이트 (PATCH /api/v1/notifications/settings)
# FCM 토큰 등록/업데이트 (POST /api/v1/notifications/fcm-token)
