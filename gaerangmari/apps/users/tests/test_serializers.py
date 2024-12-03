from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from users.models import UserProfile
from users.serializers import (
    UserCreateSerializer,
    UserDetailSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer
)

User = get_user_model()

class UserCreateSerializerTest(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123!@#",
            "password_confirm": "testpass123!@#",
            "nickname": "테스트유저"
        }

    def test_create_user(self):
        """사용자 생성 시리얼라이저 테스트"""
        serializer = UserCreateSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.nickname, self.user_data["nickname"])
        self.assertTrue(hasattr(user, 'profile'))

    def test_password_validation(self):
        """비밀번호 검증 테스트"""
        # 비밀번호 불일치
        invalid_data = {**self.user_data, "password_confirm": "wrong123!@#"}
        serializer = UserCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        
        # 비밀번호 너무 짧음
        invalid_data = {
            **self.user_data,
            "password": "123",
            "password_confirm": "123"
        }
        serializer = UserCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

class UserDetailSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123!@#",
            nickname="테스트유저"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio="테스트 프로필"
        )

    def test_user_detail_serializer(self):
        """사용자 상세정보 시리얼라이저 테스트"""
        serializer = UserDetailSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['nickname'], self.user.nickname)
        self.assertEqual(data['profile']['bio'], self.profile.bio)

    def test_update_user_detail(self):
        """사용자 정보 수정 테스트"""
        update_data = {
            "nickname": "수정된닉네임",
            "district": "강남구",
            "neighborhood": "삼성동",
            "profile": {"bio": "수정된 프로필"}
        }
        
        serializer = UserDetailSerializer(
            self.user,
            data=update_data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        
        self.assertEqual(updated_user.nickname, "수정된닉네임")
        self.assertEqual(updated_user.district, "강남구")
        self.assertEqual(updated_user.profile.bio, "수정된 프로필")

class PasswordSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123!@#",
            nickname="테스트유저"
        )

    def test_password_change_serializer(self):
        """비밀번호 변경 시리얼라이저 테스트"""
        data = {
            "current_password": "testpass123!@#",
            "new_password": "newpass123!@#",
            "new_password_confirm": "newpass123!@#"
        }
        serializer = PasswordChangeSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # 새 비밀번호 불일치
        invalid_data = {**data, "new_password_confirm": "wrong123!@#"}
        serializer = PasswordChangeSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_password_reset_serializer(self):
        """비밀번호 재설정 시리얼라이저 테스트"""
        data = {"email": "test@example.com"}
        serializer = PasswordResetSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # 존재하지 않는 이메일
        invalid_data = {"email": "nonexistent@example.com"}
        serializer = PasswordResetSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())