from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    PasswordChangeSerializer,
    PasswordResetSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    사용자 관리를 위한 ViewSet
    """

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get_permissions(self):
        if self.action in ["create", "reset_password"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return self.serializer_class

    def get_object(self):
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return self.request.user
        return super().get_object()

    @action(detail=False, methods=["post"])
    def change_password(self, request):
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

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def reset_password(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)

            # 임시 비밀번호 생성 및 이메일 발송 로직
            temp_password = User.objects.make_random_password()
            user.set_password(temp_password)
            user.save()

            # 이메일 발송 로직 구현 필요

            return Response({"message": "임시 비밀번호가 이메일로 발송되었습니다."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["patch"])
    def notification_settings(self, request):
        user = request.user
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

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
