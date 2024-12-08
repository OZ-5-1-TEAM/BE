from .base import *

# 테스트용 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

# 테스트용 이메일 설정
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 미디어 파일 설정
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')

# 비밀번호 해싱 속도 향상
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]