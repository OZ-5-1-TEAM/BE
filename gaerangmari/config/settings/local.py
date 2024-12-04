from .base import * 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# CORS 설정
CORS_ALLOW_ALL_ORIGINS = True  # 개발 환경에서만 사용
CORS_ALLOW_CREDENTIALS = True  # 개발 환경에서만 사용

VAPID_PRIVATE_KEY = 'your_vapid_private_key'
VAPID_ADMIN_EMAIL = 'admin@example.com'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

WEATHER_API_KEY="d30378026262bc1c28d337246271fd5d" #테스트용

DEFAULT_FROM_EMAIL="admin@fortest.com"

CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app"  # ngrok https URL을 신뢰할 수 있는 출처로 등록
]

