from django.urls import path

from . import views

app_name = "messages"

urlpatterns = [
    path("", views.MessageListCreateView.as_view(), name="message-list-create"),
    path(
        "received/", views.ReceivedMessageListView.as_view(), name="received-messages"
    ),
    path("sent/", views.SentMessageListView.as_view(), name="sent-messages"),
    path("<int:message_id>/", views.MessageDetailView.as_view(), name="message-detail"),
    path(
        "<int:message_id>/read/", views.MessageReadView.as_view(), name="message-read"
    ),
    path(
        "bulk-delete/",
        views.MessageBulkDeleteView.as_view(),
        name="message-bulk-delete",
    ),
]
"""
POST /api/v1/messages (쪽지 보내기)
GET /api/v1/messages/received (받은 쪽지함 조회)
GET /api/v1/messages/sent (보낸 쪽지함 조회)
PUT /api/v1/messages/{message_id}/read (쪽지 읽음 처리)
DELETE /api/v1/messages/{message_id} (쪽지 삭제)
"""
