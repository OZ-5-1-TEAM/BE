from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.PostListCreateView.as_view(), name="post-list-create"),
    path("<int:post_id>/", views.PostDetailView.as_view(), name="post-detail"),
    path(
        "<int:post_id>/comments/",
        views.CommentListCreateView.as_view(),
        name="comment-list-create",
    ),
    path(
        "<int:post_id>/comments/<int:comment_id>/",
        views.CommentDetailView.as_view(),
        name="comment-detail",
    ),
    path("<int:post_id>/like/", views.LikeView.as_view(), name="post-like"),
    path("<int:post_id>/report/", views.ReportView.as_view(), name="post-report"),
]

# 게시글 목록 조회 및 생성 (GET, POST /api/v1/posts)
# 게시글 상세 조회, 수정, 삭제 (GET, PUT, DELETE /api/v1/posts/{post_id})
# 댓글 목록 조회 및 생성 (GET, POST /api/v1/posts/{post_id}/comments)
# 댓글 상세 조회, 수정, 삭제 (GET, PUT, DELETE /api/v1/posts/{post_id}/comments/{comment_id})
# 게시글 좋아요/취소 (POST /api/v1/posts/{post_id}/like)
# 게시글/댓글 신고 (POST /api/v1/posts/{post_id}/report)
