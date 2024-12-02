from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("signup/", views.UserCreateView.as_view(), name="user-create"),
    path("me/", views.UserDetailView.as_view(), name="user-detail"),
    path("me/delete/", views.UserDeleteView.as_view(), name="user-delete"),
    path("social-login/", views.SocialLoginView.as_view(), name="social-login"),
    path(
        "password/change/", views.PasswordChangeView.as_view(), name="password-change"
    ),
    path("password/reset/", views.PasswordResetView.as_view(), name="password-reset"),
    path(
        "notifications/settings/",
        views.NotificationSettingsView.as_view(),
        name="notification-settings",
    ),
]

# 회원가입 (POST /api/v1/users/signup)
# 사용자 정보 조회/수정 (GET, PUT /api/v1/users/me)
# 회원 탈퇴 (DELETE /api/v1/users/me/delete)
# 소셜 로그인 (POST /api/v1/users/social-login)
# 비밀번호 변경 (POST /api/v1/users/password/change)
# 비밀번호 재설정 (POST /api/v1/users/password/reset)
# 알림 설정 변경 (PUT /api/v1/users/notifications/settings)