# CORS 설정
CORS_ALLOW_ALL_ORIGINS = True  # 개발 환경에서만 사용, 프로덕션에서는 특정 도메인만 허용하는 것이 좋습니다.

# 또는 특정 도메인만 허용:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:5500",
# ]

# 추가 CORS 옵션
CORS_ALLOW_CREDENTIALS = True