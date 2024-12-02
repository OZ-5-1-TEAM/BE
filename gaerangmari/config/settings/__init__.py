import os

from django.core.exceptions import ImproperlyConfigured

# 환경 변수에서 DJANGO_ENV 값을 읽어옴
DJANGO_ENV = os.getenv("DJANGO_ENV", "local")

# 환경에 따른 설정 파일 import
if DJANGO_ENV == "production":
    from .production import *
elif DJANGO_ENV == "local":
    from .local import *
else:
    raise ImproperlyConfigured(f"Unknown environment: {DJANGO_ENV}")
