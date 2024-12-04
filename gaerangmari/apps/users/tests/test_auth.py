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
