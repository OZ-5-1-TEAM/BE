from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 500,
        "CONN_HEALTH_CHECKS": True,
    }
}

# 발송용 Email 설정
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Gmail 사용 시
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Gmail 앱 비밀번호
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# AWS S3 설정
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'ap-northeast-2'  # 서울 리전
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'public-read'
AWS_LOCATION = 'media'

# S3를 기본 저장소로 설정
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'

# Social Login Settings (도메인 확정 후 설정)
# INSTALLED_APPS += ['social_django']
# SOCIAL_AUTH_REDIRECT_URI = 'https://yourdomain.com/api/auth/callback/'
# FRONTEND_BASE_URL = 'https://yourdomain.com/'

# Kakao Login Settings
# KAKAO_REST_API_KEY = ''
# KAKAO_REDIRECT_URI = f'{FRONTEND_BASE_URL}api/auth/kakao/callback'

# Google Login Settings
# GOOGLE_CLIENT_ID = ''
# GOOGLE_CLIENT_SECRET = ''
# GOOGLE_REDIRECT_URI = f'{FRONTEND_BASE_URL}api/auth/google/callback'