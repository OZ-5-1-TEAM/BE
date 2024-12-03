from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            "username": "test@example.com",
            "email": "test@example.com",
            "password": "testpass123!@#",
            "nickname": "테스트유저"
        }

    def test_create_user(self):
        """일반 사용자 생성 테스트"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.nickname, self.user_data["nickname"])
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """관리자 생성 테스트"""
        admin_user = User.objects.create_superuser(**self.user_data)
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_nickname_validation(self):
        """닉네임 유효성 검증 테스트"""
        # 닉네임이 너무 짧은 경우
        user = User(**{**self.user_data, "nickname": "a"})
        with self.assertRaises(ValidationError):
            user.full_clean()

        # 닉네임이 너무 긴 경우
        user = User(**{**self.user_data, "nickname": "a" * 11})
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_user_email_unique(self):
        """이메일 중복 검증 테스트"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            User.objects.create_user(**self.user_data)

    def test_user_status_change(self):
        """사용자 상태 변경 테스트"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.status, "active")
        
        user.status = "inactive"
        user.status_reason = "휴면 계정 전환"
        user.save()
        
        user.refresh_from_db()
        self.assertEqual(user.status, "inactive")
        self.assertEqual(user.status_reason, "휴면 계정 전환")

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123!@#",
            nickname="테스트유저"
        )

    def test_create_profile(self):
        """프로필 생성 테스트"""
        profile = UserProfile.objects.create(
            user=self.user,
            bio="안녕하세요. 테스트 사용자입니다."
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, "안녕하세요. 테스트 사용자입니다.")

    def test_profile_bio_length(self):
        """프로필 자기소개 길이 제한 테스트"""
        profile = UserProfile(
            user=self.user,
            bio="a" * 501  # 최대 500자를 초과
        )
        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_profile_str_representation(self):
        """프로필 문자열 표현 테스트"""
        profile = UserProfile.objects.create(
            user=self.user,
            bio="테스트 프로필"
        )
        self.assertEqual(str(profile), f"{self.user.nickname}의 프로필")