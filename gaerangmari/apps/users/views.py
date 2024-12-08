import secrets
import string
import random
import requests
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser

from .models import UserProfile, EmailVerification
from .serializers import (
    PasswordChangeSerializer,
    PasswordResetSerializer,
    SocialLoginSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    CustomTokenObtainPairSerializer,
    EmailVerificationSerializer
)

User = get_user_model()
class UserCreateView(generics.CreateAPIView):
    """회원가입 뷰"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # 이메일 인증 코드 생성 및 발송
            verification_code = ''.join(random.choices('0123456789', k=6))
            expires_at = timezone.now() + timedelta(minutes=30)
            
            EmailVerification.objects.create(
                user=user,
                code=verification_code,
                expires_at=expires_at
            )
            
            html_message = render_to_string('emails/email_verification.html', {
                'user': user,
                'verification_code': verification_code
            })
            plain_message = strip_tags(html_message)

            send_mail(
                subject='회원가입 이메일 인증',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message
            )
            
            return Response({
                "message": "회원가입이 완료되었습니다. 이메일로 발송된 인증 코드를 입력해주세요.",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            error_message = str(e).lower()
            if "unique constraint" in error_message:
                return Response({
                    "error": "DUPLICATE_VALUE",
                    "message": "이메일 또는 닉네임이 이미 사용 중입니다."
                }, status=status.HTTP_409_CONFLICT)  # 409 상태 코드로 변경
            return Response({
                "error": "회원가입 중 오류가 발생했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveUpdateAPIView):
    """사용자 정보 조회/수정 뷰"""
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # 파일 업로드를 위한 파서 추가

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # 파일 필드명 매핑
        if 'profilePhoto' in request.FILES:
            request.FILES['profile_image'] = request.FILES.pop('profilePhoto')
        if 'additionalPhoto' in request.FILES:
            request.FILES['additional_image'] = request.FILES.pop('additionalPhoto')

        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=partial,
            context={'request': request}  # validate 메서드에서 파일 검증을 위해 필요
        )
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except serializers.ValidationError as e:
            if 'error' in e.detail and e.detail['error'] == 'INVALID_FILE':
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            raise e

class UserDeleteView(generics.DestroyAPIView):
    """회원 탈퇴 뷰"""
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

class NotificationSettingsView(generics.UpdateAPIView):
    """알림 설정 변경 뷰"""
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        notification_fields = [
            "push_enabled",
            "message_notification",
            "friend_notification",
            "comment_notification",
            "like_notification",
        ]

        for field in notification_fields:
            if field in request.data:
                setattr(user, field, request.data[field])

        user.save()
        return Response(self.get_serializer(user).data)
    
class EmailVerificationView(APIView):
    """이메일 인증 뷰"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = serializer.validated_data['user_id']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(id=user_id)
            verification = EmailVerification.objects.filter(
                user=user,
                code=code,
                is_verified=False
            ).order_by('-created_at').first()

            if not verification:
                return Response({
                    "error": "잘못된 인증 코드입니다."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if verification.is_expired():
                return Response({
                    "error": "만료된 인증 코드입니다."
                }, status=status.HTTP_400_BAD_REQUEST)

            verification.is_verified = True
            verification.save()
            
            user.is_active = True
            user.save()

            return Response({
                "message": "이메일이 성공적으로 인증되었습니다."
            })
            
        except User.DoesNotExist:
            return Response({
                "error": "사용자를 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        

class PasswordChangeView(APIView):
    """비밀번호 변경 뷰"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get("current_password")):
                user.set_password(serializer.data.get("new_password"))
                user.save()
                return Response({
                    "message": "비밀번호가 성공적으로 변경되었습니다."
                })
            return Response({
                "error": "현재 비밀번호가 일치하지 않습니다."
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """비밀번호 재설정 뷰"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                temp_password = self.generate_temp_password()
                user.set_password(temp_password)
                user.save()

                self.send_password_reset_email(user, temp_password)
                return Response({
                    "message": "임시 비밀번호가 이메일로 발송되었습니다."
                })
            except User.DoesNotExist:
                return Response({
                    "error": "해당 이메일로 가입된 계정이 없습니다."
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_temp_password(self, length=12):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def send_password_reset_email(self, user, temp_password):
        subject = '임시 비밀번호 발급'
        html_message = render_to_string('emails/password_reset.html', {
            'user': user,
            'temp_password': temp_password
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message
        )

class SocialLoginView(APIView):
    """소셜 로그인 뷰"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        token = serializer.validated_data["access_token"]

        try:
            if provider == "kakao":
                user, created = self.process_kakao_login(token)
            elif provider == "google":
                user, created = self.process_google_login(token)
            else:
                return Response({
                    "error": "지원하지 않는 소셜 로그인입니다."
                }, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)
            user.last_login_at = timezone.now()
            user.save()

            return Response({
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": UserDetailSerializer(user).data
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "소셜 로그인 처리 중 오류가 발생했습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

    def process_kakao_login(self, access_token):
        response = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code != 200:
            raise ValueError("유효하지 않은 카카오 토큰입니다.")
            
        user_info = response.json()
        kakao_account = user_info.get("kakao_account", {})
        
        if not kakao_account.get("email"):
            raise ValueError("이메일 정보 제공에 동의해주세요.")

        kakao_id = str(user_info["id"])
        email = kakao_account["email"]
        nickname = user_info.get("properties", {}).get("nickname")

        user = User.objects.filter(
            social_id=kakao_id, 
            social_provider="kakao"
        ).first()
        
        if user:
            return user, False
            
        user = User.objects.create_user(
            username=email,
            email=email,
            nickname=nickname or f"카카오회원_{kakao_id[:8]}",
            is_social=True,
            social_provider="kakao",
            social_id=kakao_id
        )
        return user, True

    def process_google_login(self, access_token):
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code != 200:
            raise ValueError("유효하지 않은 구글 토큰입니다.")
            
        user_info = response.json()
        google_id = user_info["sub"]
        email = user_info["email"]
        nickname = user_info.get("name")

        user = User.objects.filter(
            social_id=google_id, 
            social_provider="google"
        ).first()
        
        if user:
            return user, False
            
        user = User.objects.create_user(
            username=email,
            email=email,
            nickname=nickname or f"구글회원_{google_id[:8]}",
            is_social=True,
            social_provider="google",
            social_id=google_id
        )
        return user, True


class LoginView(TokenObtainPairView):
    """로그인 뷰"""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data['email'])
            user.last_login_at = timezone.now()
            user.save()
        return response


class LogoutView(APIView):
    """로그아웃 뷰"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                "message": "로그아웃되었습니다."
            })
        except Exception:
            return Response({
                "error": "잘못된 토큰입니다."
            }, status=status.HTTP_400_BAD_REQUEST)

class EmailCheckView(APIView):
    """이메일 중복 확인 뷰"""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        
        try:
            validate_email(email)
        except ValidationError:
            return Response({
                "error": "VALIDATION_ERROR",
                "message": "유효한 이메일 형식이 아닙니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        is_available = not User.objects.filter(email=email).exists()
        return Response({"available": is_available})


class NicknameCheckView(APIView):
    """닉네임 중복 확인 뷰"""
    permission_classes = [AllowAny]

    def post(self, request):
        nickname = request.data.get('nickname')
        
        if not nickname:
            return Response({
                "error": "VALIDATION_ERROR",
                "message": "닉네임을 입력해주세요."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not (2 <= len(nickname) <= 10):
            return Response({
                "error": "VALIDATION_ERROR",
                "message": "닉네임은 2~10자 사이여야 합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        is_available = not User.objects.filter(nickname=nickname).exists()
        return Response({"available": is_available})