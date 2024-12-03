from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WeatherViewSet

router = DefaultRouter()
router.register(r'weather', WeatherViewSet, basename='weather')

urlpatterns = [
    path('', include(router.urls)),
]


# 날씨 데이터 목록 조회 (GET /api/v1/weathers/)
# 특정 날씨 데이터 조회 (GET /api/v1/weathers/<id>/)
# 현재 날씨 데이터 조회 (GET /api/v1/weathers/current/?district=서울)