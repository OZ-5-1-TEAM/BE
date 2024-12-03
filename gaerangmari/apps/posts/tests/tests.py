from django.test import TransactionTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from ..models import Post, Comment, Like, Report, PostImage
from ..serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostCreateSerializer,
    CommentSerializer,
    ReportSerializer
)

User = get_user_model()

class PostTestCase(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test1234!',
            nickname='테스트유저',
            district='강남구',
            neighborhood='역삼동',
            profile_image=None
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin1234!',
            nickname='관리자',
            district='강남구',
            neighborhood='역삼동',
            is_staff=True,
            profile_image=None
        )
        self.post = Post.objects.create(
            title='테스트 게시글',
            content='테스트 내용',
            author=self.user,
            category='community',
            district='강남구',
            neighborhood='역삼동'
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='테스트 댓글'
        )
        self.like = Like.objects.create(post=self.post, user=self.user)
        self.post.likes_count = 1  # 직접 likes_count 설정
        self.post.save()

    def tearDown(self):
        Post.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        User.objects.all().delete()

class PostModelTest(PostTestCase):
    def test_create_post(self):
        post = Post.objects.create(
            title='새 게시글',
            content='새 내용',
            author=self.user,
            category='community',
            district='강남구',
            neighborhood='역삼동'
        )
        self.assertEqual(post.title, '새 게시글')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.views, 0)
        self.assertEqual(post.likes_count, 0)
        self.assertEqual(post.comments_count, 0)
        self.assertFalse(post.is_deleted)

    def test_create_comment(self):
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='새 댓글',
            parent=None
        )
        self.assertEqual(comment.content, '새 댓글')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertFalse(comment.is_deleted)

class PostViewTest(PostTestCase):
    def test_list_posts(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('posts:post-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.post.title)

    def test_create_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('posts:post-list-create')
        data = {
            'title': '새 게시글',
            'content': '내용',
            'category': 'community',
            'district': '강남구',
            'neighborhood': '역삼동'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)

    def test_create_comment(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('posts:comment-list-create', kwargs={'post_id': self.post.id})
        data = {'content': '새 댓글'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(content='새 댓글').exists())

    def test_toggle_like(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('posts:post-like', kwargs={'post_id': self.post.id})
        
        # First request should remove the like (since it was created in setUp)
        initial_likes = self.post.likes_count
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, max(0, initial_likes - 1))
        self.assertFalse(response.data['is_liked'])
        
        # Second request should create a new like
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, initial_likes)
        self.assertTrue(response.data['is_liked'])

    def test_report_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('posts:post-report', kwargs={'post_id': self.post.id})
        data = {
            'post': self.post.id,
            'reason': 'spam',
            'description': '테스트 신고'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)