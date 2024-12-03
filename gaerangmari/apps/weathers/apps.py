from django.apps import AppConfig

class WeathersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # 기본 자동 필드 타입 설정
    name = 'weathers'  # 앱 이름
    verbose_name = 'Weather Application'  # 관리자 페이지에서 사용할 앱의 표시 이름 (선택 사항)