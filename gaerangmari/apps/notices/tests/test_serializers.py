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
            email='admin@test.com',
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

        # 올바른 이미지 파일 생성
        from io import BytesIO
        from PIL import Image
        
        image = Image.new('RGB', (100, 100))
        temp_file = BytesIO()
        image.save(temp_file, 'JPEG')
        temp_file.seek(0)
        
        image_file = SimpleUploadedFile(
            "test_image.jpg",
            temp_file.read(),
            content_type="image/jpeg"
        )
        
        data = {
            'title': 'New Notice',
            'content': 'New Content',
            'is_pinned': True,
            'author': self.user.id,
            'images': [image_file]
        }
        
        serializer = NoticeCreateSerializer(
            data=data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            print(serializer.errors)  # 디버깅을 위한 에러 출력
            
        self.assertTrue(serializer.is_valid())