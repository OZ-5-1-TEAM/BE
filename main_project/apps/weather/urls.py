from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import WeatherViewSet

router = DefaultRouter()
router.register(r'weather', WeatherViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]