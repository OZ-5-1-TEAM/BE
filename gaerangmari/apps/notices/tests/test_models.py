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
            email='admin@test.com',
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
            email='reader@test.com',
            password='reader123',
            nickname='Reader'
        )
        read = NoticeRead.objects.create(
            notice=self.notice,
            user=reader
        )
        self.assertTrue(isinstance(read, NoticeRead))