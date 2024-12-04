import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import EmailVerification

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        nickname='testuser'
    )

@pytest.fixture
def auth_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client

class TestUserCreateView:
    def test_create_user_success(self, api_client):
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'nickname': 'newuser'
        }
        response = api_client.post('/api/v1/users/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user_id' in response.data
        assert '이메일로 발송된 인증 코드를 입력해주세요' in response.data['message']
        
        # 이메일 발송 확인 (콘솔 출력 확인)
        user = User.objects.get(email='newuser@example.com')
        verification = user.emailverification_set.first()
        assert verification is not None
        assert not verification.is_expired()

    def test_create_user_duplicate_email(self, api_client, test_user):
        data = {
            'email': 'test@example.com',  # 이미 존재하는 이메일
            'password': 'newpass123',
            'nickname': 'newuser'
        }
        response = api_client.post('/api/v1/users/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '이미 사용 중인 이메일입니다' in response.data['error']

class TestEmailVerificationView:
    def test_verify_email_success(self, api_client):
        # 테스트용 사용자와 인증 코드 생성
        user = User.objects.create_user(
            email='verify@example.com',
            password='testpass123',
            nickname='verifyuser',
            is_active=False
        )
        verification = user.emailverification_set.create(
            code='123456',
            expires_at=timezone.now() + timezone.timedelta(minutes=30)
        )
        
        data = {
            'user_id': user.id,
            'code': '123456'
        }
        response = api_client.post('/api/v1/users/verify-email/', data)
        assert response.status_code == status.HTTP_200_OK
        assert '이메일이 성공적으로 인증되었습니다' in response.data['message']
        
        # 사용자 상태 확인
        user.refresh_from_db()
        assert user.is_active

class TestPasswordChangeView:
    def test_change_password_success(self, auth_client, test_user):
        data = {
            'current_password': 'testpass123',
            'new_password': 'newtestpass123'
        }
        response = auth_client.post('/api/v1/users/password/change/', data)
        assert response.status_code == status.HTTP_200_OK
        assert '비밀번호가 성공적으로 변경되었습니다' in response.data['message']
        
        # 새 비밀번호로 로그인 확인
        test_user.refresh_from_db()
        assert test_user.check_password('newtestpass123')

    def test_change_password_wrong_current(self, auth_client):
        data = {
            'current_password': 'wrongpass',
            'new_password': 'newtestpass123'
        }
        response = auth_client.post('/api/v1/users/password/change/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '현재 비밀번호가 일치하지 않습니다' in response.data['error']

class TestPasswordResetView:
    def test_reset_password_success(self, api_client, test_user):
        data = {'email': 'test@example.com'}
        response = api_client.post('/api/v1/users/password/reset/', data)
        assert response.status_code == status.HTTP_200_OK
        assert '임시 비밀번호가 이메일로 발송되었습니다' in response.data['message']

    def test_reset_password_invalid_email(self, api_client):
        data = {'email': 'nonexistent@example.com'}
        response = api_client.post('/api/v1/users/password/reset/', data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert '해당 이메일로 가입된 계정이 없습니다' in response.data['error']

class TestUserDetailView:
    def test_get_user_detail(self, auth_client, test_user):
        response = auth_client.get('/api/v1/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == test_user.email
        assert response.data['nickname'] == test_user.nickname

    def test_update_user_detail(self, auth_client, test_user):
        data = {'nickname': 'updated_nickname'}
        response = auth_client.patch('/api/v1/users/me/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nickname'] == 'updated_nickname'
        
        test_user.refresh_from_db()
        assert test_user.nickname == 'updated_nickname'

    def test_update_profile_image(self, auth_client, test_user):
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # 테스트용 이미지 파일 생성
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  # 빈 이미지
            content_type='image/jpeg'
        )
        
        response = auth_client.patch(
            '/api/v1/users/me/',
            {'profile_image': image},
            format='multipart'
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'profile_image' in response.data

class TestNotificationSettingsView:
    def test_update_notification_settings(self, auth_client, test_user):
        data = {
            'push_enabled': True,
            'message_notification': False,
            'friend_notification': True,
            'comment_notification': False,
            'like_notification': True
        }
        response = auth_client.patch('/api/v1/users/notifications/', data)
        assert response.status_code == status.HTTP_200_OK
        
        test_user.refresh_from_db()
        for field, value in data.items():
            assert getattr(test_user, field) == value

class TestLoginView:
    def test_login_success(self, api_client, test_user):
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = api_client.post('/api/v1/users/login/', data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_invalid_credentials(self, api_client):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        response = api_client.post('/api/v1/users/login/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestLogoutView:
    def test_logout_success(self, auth_client):
        # 로그인하고 받은 리프레시 토큰으로 테스트
        refresh_token = RefreshToken.for_user(test_user)
        data = {'refresh_token': str(refresh_token)}
        
        response = auth_client.post('/api/v1/users/logout/', data)
        assert response.status_code == status.HTTP_200_OK
        assert '로그아웃되었습니다' in response.data['message']

    def test_logout_invalid_token(self, auth_client):
        data = {'refresh_token': 'invalid_token'}
        response = auth_client.post('/api/v1/users/logout/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '잘못된 토큰입니다' in response.data['error']

class TestUserDeleteView:
    def test_user_delete_success(self, auth_client, test_user):
        response = auth_client.delete('/api/v1/users/me/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        test_user.refresh_from_db()
        assert not test_user.is_active

    def test_user_delete_unauthorized(self, api_client):
        response = api_client.delete('/api/v1/users/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestTokenRefresh:
    def test_token_refresh_success(self, api_client, test_user):
        # 초기 토큰 발급
        refresh = RefreshToken.for_user(test_user)
        
        data = {'refresh': str(refresh)}
        response = api_client.post('/api/token/refresh/', data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_token_refresh_invalid(self, api_client):
        data = {'refresh': 'invalid_token'}
        response = api_client.post('/api/token/refresh/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_user_full_flow(api_client):
    # 1. 회원가입
    signup_data = {
        'email': 'flow@example.com',
        'password': 'flowpass123',
        'nickname': 'flowuser'
    }
    response = api_client.post('/api/v1/users/', signup_data)
    assert response.status_code == status.HTTP_201_CREATED
    user_id = response.data['user_id']

    # 2. 이메일 인증
    verification = EmailVerification.objects.get(user_id=user_id)
    verify_data = {
        'user_id': user_id,
        'code': verification.code
    }
    response = api_client.post('/api/v1/users/verify-email/', verify_data)
    assert response.status_code == status.HTTP_200_OK

    # 3. 로그인
    login_data = {
        'email': 'flow@example.com',
        'password': 'flowpass123'
    }
    response = api_client.post('/api/v1/users/login/', login_data)
    assert response.status_code == status.HTTP_200_OK
    tokens = response.data

    # 4. 인증된 요청 테스트
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    response = api_client.get('/api/v1/users/me/')
    assert response.status_code == status.HTTP_200_OK