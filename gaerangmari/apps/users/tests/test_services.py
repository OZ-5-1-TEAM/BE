from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from users.services import SocialLoginService, PasswordService
from unittest.mock import ANY

User = get_user_model()

class SocialLoginServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123!@#",
            nickname="테스트유저"
        )

    @patch('requests.get')
    def test_process_kakao_login_existing_user(self, mock_get):
        """기존 카카오 회원 로그인 테스트"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "12345",
            "kakao_account": {"email": "test@example.com"},
            "properties": {"nickname": "카카오닉네임"}
        }
        mock_get.return_value = mock_response

        self.user.is_social = True
        self.user.social_provider = "kakao"
        self.user.social_id = "12345"
        self.user.save()

        user, created = SocialLoginService.process_kakao_login("fake_token")
        self.assertEqual(user.email, "test@example.com")
        self.assertFalse(created)

    @patch('requests.get')
    def test_process_kakao_login_new_user(self, mock_get):
        """새로운 카카오 회원 로그인 테스트"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "67890",
            "kakao_account": {"email": "new@example.com"},
            "properties": {"nickname": "새카카오유저"}
        }
        mock_get.return_value = mock_response

        user, created = SocialLoginService.process_kakao_login("fake_token")
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(created)
        self.assertEqual(user.social_provider, "kakao")

class PasswordServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123!@#",
            nickname="테스트유저"
        )

    def test_generate_temp_password(self):
        """임시 비밀번호 생성 테스트"""
        password = PasswordService.generate_temp_password()
        self.assertEqual(len(password), 12)  # 기본 길이 확인
        password = PasswordService.generate_temp_password(length=16)
        self.assertEqual(len(password), 16)  # 커스텀 길이 확인

    @patch('django.core.email.send_mail')
    def test_send_temp_password_email(self, mock_send):
        """임시 비밀번호 이메일 발송 테스트"""
        mock_send.return_value = 1  # 이메일 발송 성공 시뮬레이션
        temp_password = "temp123!@#"
        PasswordService.send_temp_password_email(self.user, temp_password)
        mock_send.assert_called_once()
        mock_send.assert_called_with(
        subject='임시 비밀번호가 발급되었습니다',
        message=ANY,  # 메시지 내용은 정확히 검증하지 않음
        from_email=ANY,
        recipient_list=[self.user.email]
    )