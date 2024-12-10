from common.permissions import IsOwner, IsAdmin
from django.db.models import F
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from common.pagination import StandardResultsSetPagination
from common.response import CustomResponse
from rest_framework.exceptions import NotFound
from .models import Comment, Like, Post
from .serializers import (
    CommentCreateSerializer,
    PostCreateSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostUpdateSerializer,
    ReportSerializer,
)


from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 20
    
    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view)
        except NotFound:
            return []
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count if hasattr(self, 'page') else 0,
            'results': data
        })
        
class PostListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostListSerializer

    def get_queryset(self):
        queryset = Post.objects.filter(is_deleted=False)
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset.order_by('-created_at')
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class LikedPostListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostListSerializer

    def get_queryset(self):
        return Post.objects.filter(
            likes__user=self.request.user,
            is_deleted=False
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return CustomResponse.error(message="게시물이 없습니다.", status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            data={"posts": serializer.data},
            status=status.HTTP_200_OK
        )


class PostDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostDetailSerializer
    lookup_url_kwarg = "post_id"

    def get_queryset(self):
        return Post.objects.filter(is_deleted=False)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.views = F("views") + 1
            instance.save()
            instance.refresh_from_db()
            serializer = self.get_serializer(instance)
            return CustomResponse.success(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except Post.DoesNotExist:
            return CustomResponse.error(
                message="게시글을 찾을 수 없습니다.",
                status=status.HTTP_404_NOT_FOUND
            )


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.error(
                message="잘못된 요청입니다.",
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comment = serializer.save(
            author=request.user,
            post_id=self.kwargs["post_id"]
        )
        return CustomResponse.success(
            status=status.HTTP_201_CREATED
        )


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_deleted=False)
        
        try:
            like = Like.objects.get(post=post, user=request.user)
            like.delete()
            post.likes_count = max(0, post.likes_count - 1)
            post.save()
            return CustomResponse.success(
                data={"is_liked": False, "likes_count": post.likes_count},
                status=status.HTTP_200_OK
            )
        except Like.DoesNotExist:
            Like.objects.create(post=post, user=request.user)
            post.likes_count += 1
            post.save()
            return CustomResponse.success(
                data={"is_liked": True, "likes_count": post.likes_count},
                status=status.HTTP_200_OK
            )


class ReportView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.error(
                message="잘못된 요청입니다.",
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(reporter=request.user)
        return CustomResponse.success(
            status=status.HTTP_201_CREATED
        )