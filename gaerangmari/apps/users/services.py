import secrets
import string
from typing import Any, Tuple

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

User = get_user_model()

class SocialLoginService:
    @staticmethod
    def process_kakao_login(access_token: str) -> Tuple[Any, bool]:
        """
        카카오 로그인 처리
        Returns: (user, created) 튜플
        """
        # 카카오 사용자 정보 가져오기
        user_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        kakao_id = str(user_info["id"])
        email = user_info["kakao_account"].get("email")
        nickname = user_info["properties"].get("nickname")

        if not email:
            raise ValueError("이메일 정보 제공에 동의해주세요.")

        # 기존 회원인지 확인
        user = User.objects.filter(social_id=kakao_id, social_provider="kakao").first()
        
        if user:
            created = False
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                nickname=nickname or f"카카오회원_{kakao_id[:8]}",
                is_social=True,
                social_provider="kakao",
                social_id=kakao_id
            )
            created = True
        
        return user, created

    @staticmethod
    def process_google_login(access_token: str) -> Tuple[Any, bool]:
        """
        구글 로그인 처리
        Returns: (user, created) 튜플
        """
        # 구글 사용자 정보 가져오기
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        google_id = user_info["sub"]
        email = user_info["email"]
        nickname = user_info.get("name")

        # 기존 회원인지 확인
        user = User.objects.filter(social_id=google_id, social_provider="google").first()
        
        if user:
            created = False
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                nickname=nickname or f"구글회원_{google_id[:8]}",
                is_social=True,
                social_provider="google",
                social_id=google_id
            )
            created = True
        
        return user, created

class PasswordService:
    @staticmethod
    def generate_temp_password(length: int = 12) -> str:
        """임시 비밀번호 생성"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(length))

    @staticmethod
    def send_temp_password_email(user, temp_password):
        subject = '임시 비밀번호가 발급되었습니다'
        message = f'임시 비밀번호: {temp_password}\n로그인 후 반드시 비밀번호를 변경해주세요.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list
        )