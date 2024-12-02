from common.permissions import IsOwner
from django.db.models import F
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Comment, Like, Post
from .serializers import (
    CommentSerializer,
    PostCreateSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostUpdateSerializer,
    ReportSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """게시글 관리를 위한 ViewSet"""

    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "post_id"

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
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostDetailSerializer
        elif self.action == "create":
            return PostCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return PostUpdateSerializer
        return PostDetailSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views = F("views") + 1
        instance.save()
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def like(self, request, post_id=None):
        post = self.get_object()
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

    @action(detail=True, methods=["post"])
    def report(self, request, post_id=None):
        serializer = ReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reporter=request.user, post=self.get_object())
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    """댓글 관리를 위한 ViewSet"""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs["post_id"], is_deleted=False)

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post_id=self.kwargs["post_id"])

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

    @action(detail=True, methods=["post"])
    def report(self, request, post_id=None, comment_id=None):
        serializer = ReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reporter=request.user, comment=self.get_object())
        return Response(serializer.data, status=status.HTTP_201_CREATED)
