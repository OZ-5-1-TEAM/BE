from django.urls import path

from . import views

app_name = "friends"

urlpatterns = [
    path(
        "requests/",
        views.FriendRequestCreateView.as_view(),
        name="friend-request-create",
    ),
    path(
        "requests/<int:request_id>/",
        views.FriendRequestResponseView.as_view(),
        name="friend-request-response",
    ),
    path("", views.FriendListView.as_view(), name="friend-list"),
    path("<int:friend_id>/", views.FriendDetailView.as_view(), name="friend-detail"),
    path(
        "requests/pending/",
        views.PendingRequestListView.as_view(),
        name="pending-requests",
    ),
    path("requests/sent/", views.SentRequestListView.as_view(), name="sent-requests"),
]

# 친구 요청 보내기 (POST /api/v1/friends/requests)
# 친구 요청 응답 (PUT /api/v1/friends/requests/{request_id})
# 친구 목록 조회 (GET /api/v1/friends)
# 친구 상세 정보 조회 및 삭제 (GET, DELETE /api/v1/friends/{friend_id})
# 받은 친구 요청 목록 조회 (GET /api/v1/friends/requests/pending)
# 보낸 친구 요청 목록 조회 (GET /api/v1/friends/requests/sent)
