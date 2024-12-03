from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from weathers.models import WeatherData

class WeatherViewSetTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        WeatherData.objects.create(
            district="서울",
            neighborhood="강남",
            temperature=25.0,
            humidity=60.0,
            wind_speed=5.0,
            precipitation=0.0,
            precipitation_type="none",
            walking_score=80,
            forecast_time="2024-12-03T10:00:00Z"
        )

    def test_get_weather_data(self):
        response = self.client.get(reverse('weather-detail', args=[1]))  # ID가 1인 날씨 데이터 조회
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "서울")

    def test_get_current_weather(self):
        response = self.client.get(reverse('weather-current') + '?district=서울')
        self.assertEqual(response.status_code, status.HTTP_200_OK)