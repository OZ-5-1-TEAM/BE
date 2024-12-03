from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class AuthenticationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123!@#",
            nickname="테스트유저"
        )
        self.password_change_url = reverse('users:password-change')
        self.password_reset_url = reverse('users:password-reset')
        self.social_login_url = reverse('users:social-login')

    def test_password_change(self):
        """비밀번호 변경 테스트"""
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "testpass123!@#",
            "new_password": "newtestpass123!@#",
            "new_password_confirm": "newtestpass123!@#"
        }
        response = self.client.post(self.password_change_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newtestpass123!@#"))

    def test_password_reset(self):
        """비밀번호 재설정 테스트"""
        # 고유한 이메일로 테스트 유저 생성
        test_email = "unique_test@example.com"
        self.user = User.objects.create_user(
            username='unique_testuser',
            email=test_email,
            password='testpass123',
            nickname='Test User'
        )
        
        data = {"email": test_email}
        with patch('users.services.PasswordService.generate_temp_password') as mock_gen:
            mock_gen.return_value = "temp123!@#"
            with patch('django.core.email.send_mail') as mock_send:
                mock_send.return_value = 1
                response = self.client.post(self.password_reset_url, data)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertTrue(mock_send.called)

    @patch('users.services.SocialLoginService.process_kakao_login')
    def test_kakao_login(self, mock_kakao):
        """카카오 로그인 테스트"""
        mock_kakao.return_value = (self.user, False)
        data = {
            "provider": "kakao",
            "access_token": "fake_token"  # code 대신 access_token 사용
        }
        response = self.client.post(self.social_login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('users.services.SocialLoginService.process_google_login')
    def test_google_login(self, mock_google):
        """구글 로그인 테스트"""
        mock_google.return_value = (self.user, False)
        data = {
            "provider": "google",
            "access_token": "fake_token"
        }
        response = self.client.post(self.social_login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_social_provider(self):
        """잘못된 소셜 로그인 제공자 테스트"""
        data = {
            "provider": "invalid",
            "access_token": "fake_token"
        }
        response = self.client.post(self.social_login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)