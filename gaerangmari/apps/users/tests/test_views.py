from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserViewTest(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123!@#",
            "password_confirm": "testpass123!@#",
            "nickname": "테스트유저"
        }
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123!@#",
            nickname="테스트유저"
        )

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def test_user_signup(self):
        """회원가입 테스트"""
        url = reverse('users:user-create')
        data = {
            "email": "new@example.com",
            "password": "newpass123!@#",
            "password_confirm": "newpass123!@#",
            "nickname": "새유저"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_user_signup_invalid_password(self):
        """유효하지 않은 비밀번호로 회원가입 시도"""
        url = reverse('users:user-create')
        data = {
            "email": "new@example.com",
            "password": "123",  # 너무 짧은 비밀번호
            "password_confirm": "123",
            "nickname": "새유저"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_detail_get(self):
        """사용자 정보 조회 테스트"""
        url = reverse('users:user-detail')
        token = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token["access"]}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_user_detail_update(self):
        """사용자 정보 수정 테스트"""
        url = reverse('users:user-detail')
        token = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token["access"]}')
        data = {
            "nickname": "수정된닉네임",
            "district": "강남구",
            "neighborhood": "삼성동"
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], "수정된닉네임")
        self.assertEqual(response.data['district'], "강남구")

    def test_user_delete(self):
        """회원 탈퇴 테스트"""
        url = reverse('users:user-delete')
        token = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token["access"]}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user = User.objects.get(id=self.user.id)
        self.assertFalse(user.is_active)

    def test_notification_settings_update(self):
        """알림 설정 변경 테스트"""
        url = reverse('users:notification-settings')
        token = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token["access"]}')
        data = {
            "push_enabled": False,
            "message_notification": False,
            "comment_notification": False
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['push_enabled'], False)
        self.assertEqual(response.data['message_notification'], False)
        self.assertEqual(response.data['comment_notification'], False)