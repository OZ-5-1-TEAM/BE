from django.urls import path

from . import views

app_name = "friends"

urlpatterns = [
    path(
        "request/",  # requests/ → request/로 변경
        views.FriendRequestCreateView.as_view(),
        name="friend-request-create",
    ),
    path(
        "<int:friend_id>/",  # requests/<int:request_id>/ → <int:friend_id>/로 변경
        views.FriendRequestResponseView.as_view(),
        name="friend-request-response",
    ),
    path("", views.FriendListView.as_view(), name="friend-list"),
    path(
        "requests/pending/",
        views.PendingRequestListView.as_view(),
        name="pending-requests",
    ),
    path("requests/sent/", views.SentRequestListView.as_view(), name="sent-requests"),
]