from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    # GET, POST /api/v1/posts - 게시글 목록 조회 및 생성
    path("", views.PostListCreateView.as_view(), name="post-list-create"),
    
    # GET /api/v1/posts/liked - 좋아요한 게시물 목록 조회
    path("liked/", views.LikedPostListView.as_view(), name="liked-posts"),
    
    # GET /api/v1/posts/{post_id} - 게시글 상세 조회
    path("<int:post_id>/", views.PostDetailView.as_view(), name="post-detail"),
    
    # POST /api/v1/posts/{post_id}/comments - 게시글 댓글 작성
    path("<int:post_id>/comments/", views.CommentCreateView.as_view(), name="comment-create"),
    
    # POST /api/v1/posts/{post_id}/like - 게시글 좋아요/취소
    path("<int:post_id>/like/", views.LikeView.as_view(), name="post-like"),
    
    # POST /api/v1/posts/{post_id}/report - 게시글 신고
    path("<int:post_id>/report/", views.ReportView.as_view(), name="post-report"),
]