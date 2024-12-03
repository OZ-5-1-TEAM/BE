# tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from ..models import Notice, NoticeImage, NoticeFile, NoticeRead

User = get_user_model()

class NoticeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            password='admin123',
            nickname='Admin User',
            is_staff=True
        )
        self.notice = Notice.objects.create(
            title='Test Notice',
            content='Test Content',
            author=self.user,
            is_pinned=True
        )

    def test_notice_creation(self):
        self.assertTrue(isinstance(self.notice, Notice))
        self.assertEqual(str(self.notice), 'Test Notice')
        self.assertEqual(self.notice.views, 0)
        self.assertTrue(self.notice.is_pinned)

    def test_notice_image_creation(self):
        image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        image = NoticeImage.objects.create(
            notice=self.notice,
            image=image_file,
            order=0
        )
        self.assertEqual(str(image), f"{self.notice.title}의 이미지 0")

    def test_notice_file_creation(self):
        test_file = SimpleUploadedFile(
            "test.txt",
            b"file_content",
            content_type="text/plain"
        )
        file = NoticeFile.objects.create(
            notice=self.notice,
            file=test_file,
            filename="test.txt",
            file_size=len(b"file_content")
        )
        self.assertEqual(file.download_count, 0)

    def test_notice_read_creation(self):
        reader = User.objects.create_user(
            username='reader',
            password='reader123',
            nickname='Reader'
        )
        read = NoticeRead.objects.create(
            notice=self.notice,
            user=reader
        )
        self.assertTrue(isinstance(read, NoticeRead))


# tests/test_serializers.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from ..models import Notice
from ..serializers import (
    NoticeCreateSerializer,
    NoticeDetailSerializer,
    NoticeListSerializer
)

User = get_user_model()

class NoticeSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            password='admin123',
            nickname='Admin User',
            is_staff=True
        )
        self.notice = Notice.objects.create(
            title='Test Notice',
            content='Test Content',
            author=self.user
        )
        self.factory = APIRequestFactory()

    def test_notice_list_serializer(self):
        serializer = NoticeListSerializer(instance=self.notice)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test Notice')
        self.assertEqual(data['author_nickname'], self.user.nickname)

    def test_notice_detail_serializer(self):
        request = self.factory.get('/')
        request.user = self.user
        
        serializer = NoticeDetailSerializer(
            instance=self.notice,
            context={'request': request}
        )
        data = serializer.data
        
        self.assertEqual(data['content'], 'Test Content')
        self.assertEqual(data['is_read'], False)

    def test_notice_create_serializer(self):
        request = self.factory.post('/')
        request.user = self.user

        image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        
        data = {
            'title': 'New Notice',
            'content': 'New Content',
            'images': [image_file],
            'is_pinned': True
        }
        
        serializer = NoticeCreateSerializer(
            data=data,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid())


# tests/test_views.py
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from ..models import Notice, NoticeFile

User = get_user_model()

class NoticeViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            nickname='Admin User',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normal',
            password='normal123',
            nickname='Normal User'
        )
        
        self.notice = Notice.objects.create(
            title='Test Notice',
            content='Test Content',
            author=self.admin_user
        )

    def test_notice_list_view(self):
        url = reverse('notice-list')  # URL 패턴명 확인 필요
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # 검색 테스트
        response = self.client.get(f"{url}?search=Test")
        self.assertEqual(len(response.data), 1)

    def test_notice_detail_view(self):
        url = reverse('notice-detail', kwargs={'notice_id': self.notice.id})
        
        # 조회수 증가 테스트
        initial_views = self.notice.views
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notice.refresh_from_db()
        self.assertEqual(self.notice.views, initial_views + 1)

    def test_notice_create_view(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('notice-create')
        
        data = {
            'title': 'New Notice',
            'content': 'New Content',
            'is_pinned': True
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 일반 사용자 접근 테스트
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_notice_file_download(self):
        # 파일 생성
        test_file = SimpleUploadedFile(
            "test.txt",
            b"file_content",
            content_type="text/plain"
        )
        notice_file = NoticeFile.objects.create(
            notice=self.notice,
            file=test_file,
            filename="test.txt",
            file_size=len(b"file_content")
        )
        
        url = reverse('notice-file-download', kwargs={
            'notice_id': self.notice.id,
            'file_id': notice_file.id
        })
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        notice_file.refresh_from_db()
        self.assertEqual(notice_file.download_count, 1)