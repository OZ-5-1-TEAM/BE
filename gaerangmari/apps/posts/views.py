from common.permissions import IsOwner
from django.db.models import F
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Like, Post
from .serializers import (
    CommentSerializer,
    PostCreateSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostUpdateSerializer,
    ReportSerializer,
)


class PostListCreateView(generics.ListCreateAPIView):
    """게시글 목록 조회 및 생성"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Post.objects.filter(is_deleted=False)

        # 카테고리 필터링
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)

        # 지역 필터링
        district = self.request.query_params.get("district")
        if district:
            queryset = queryset.filter(district=district)

        neighborhood = self.request.query_params.get("neighborhood")
        if neighborhood:
            queryset = queryset.filter(neighborhood=neighborhood)

        # 강아지 크기 필터링
        dog_size = self.request.query_params.get("dog_size")
        if dog_size:
            queryset = queryset.filter(dog_size=dog_size)

        # 검색
        keyword = self.request.query_params.get("keyword")
        if keyword:
            queryset = queryset.filter(title__icontains=keyword) | queryset.filter(
                content__icontains=keyword
            )

        # 정렬
        sort = self.request.query_params.get("sort", "latest")
        if sort == "popular":
            queryset = queryset.order_by("-likes_count", "-created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """게시글 상세 조회, 수정, 삭제"""

    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "post_id"

    def get_queryset(self):
        return Post.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PostDetailSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return PostUpdateSerializer
        return PostDetailSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views = F("views") + 1
        instance.save()
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()


class CommentListCreateView(generics.ListCreateAPIView):
    """댓글 목록 조회 및 생성"""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(
            post_id=self.kwargs["post_id"], parent=None, is_deleted=False
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post_id=self.kwargs["post_id"])


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """댓글 상세 조회, 수정, 삭제"""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs["post_id"], is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()


class LikeView(APIView):
    """게시글 좋아요/취소"""

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = generics.get_object_or_404(Post, id=post_id, is_deleted=False)
        like, created = Like.objects.get_or_create(post=post, user=request.user)

        if not created:
            like.delete()
            post.likes_count = F("likes_count") - 1
            post.save()
            return Response({"is_liked": False, "likes_count": post.likes_count})

        post.likes_count = F("likes_count") + 1
        post.save()
        post.refresh_from_db()
        return Response({"is_liked": True, "likes_count": post.likes_count})


class ReportView(generics.CreateAPIView):
    """게시글/댓글 신고"""

    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
