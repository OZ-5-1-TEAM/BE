from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.crypto import get_random_string

def generate_temp_password(length=12):
    return get_random_string(length=length)


from .models import UserProfile
from .serializers import (
    PasswordChangeSerializer,
    PasswordResetSerializer,
    SocialLoginSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
)

User = get_user_model()


class UserCreateView(generics.CreateAPIView):
    """
    회원가입 뷰
    """

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    사용자 정보 조회/수정 뷰
    """

    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDeleteView(generics.DestroyAPIView):
    """
    회원 탈퇴 뷰
    """

    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class SocialLoginView(APIView):
    """
    소셜 로그인 뷰
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        token = serializer.validated_data["access_token"]

        # 소셜 로그인 처리 로직
        try:
            if provider == "kakao":
                user = self.process_kakao_login(token)
            elif provider == "google":
                user = self.process_google_login(token)
            else:
                return Response(
                    {"error": "지원하지 않는 소셜 로그인입니다."}, status=status.HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken.for_user(user)
            user.last_login_at = timezone.now()
            user.save()

            return Response(
                {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": UserDetailSerializer(user).data,
                }
            )

        except Exception as e:
            return Response(
                {"error": "소셜 로그인 처리 중 오류가 발생했습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

    def process_kakao_login(self, token):
        # 카카오 로그인 처리 로직 구현
        pass

    def process_google_login(self, token):
        # 구글 로그인 처리 로직 구현
        pass


class PasswordChangeView(APIView):
    """
    비밀번호 변경 뷰
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get("current_password")):
                user.set_password(serializer.data.get("new_password"))
                user.save()
                return Response({"message": "비밀번호가 성공적으로 변경되었습니다."})
            return Response(
                {"error": "현재 비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """
    비밀번호 재설정 뷰
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)

            # 임시 비밀번호 생성 및 이메일 발송 로직
            temp_password = generate_temp_password()
            user.set_password(temp_password)
            user.save()

            # 이메일 발송 로직 구현 필요

            return Response({"message": "임시 비밀번호가 이메일로 발송되었습니다."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationSettingsView(generics.UpdateAPIView):
    """
    알림 설정 변경 뷰
    """

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
