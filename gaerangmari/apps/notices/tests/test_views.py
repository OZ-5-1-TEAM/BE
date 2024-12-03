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
            email='admin@test.com',
            password='admin123',
            nickname='Admin User',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normal',
            email='normal@test.com',
            password='normal123',
            nickname='Normal User'
        )
        
        self.notice = Notice.objects.create(
            title='Test Notice',
            content='Test Content',
            author=self.admin_user
        )

    def test_notice_list_view(self):
        url = reverse('notices:notice-list')  # URL 패턴명 수정
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # 검색 테스트
        response = self.client.get(f"{url}?search=Test")
        self.assertEqual(len(response.data), 1)

    def test_notice_detail_view(self):
        url = reverse('notices:notice-detail', kwargs={'notice_id': self.notice.id})  # notice_id로 수정
        
        # 조회수 증가 테스트
        initial_views = self.notice.views
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notice.refresh_from_db()
        self.assertEqual(self.notice.views, initial_views + 1)

    def test_notice_create_view(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('notices:notice-create')
        
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
        
        url = reverse('notices:notice-file-download', kwargs={  # URL 패턴명과 매개변수 수정
            'notice_id': self.notice.id,
            'file_id': notice_file.id
        })
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        notice_file.refresh_from_db()
        self.assertEqual(notice_file.download_count, 1)