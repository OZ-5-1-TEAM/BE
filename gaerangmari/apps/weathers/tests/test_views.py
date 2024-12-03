from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from weathers.models import WeatherData
import json

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

    @patch('weathers.services.WeatherService.get_weather_data')
    def test_get_current_weather(self, mock_get_weather_data):
        mock_weather_data = WeatherData(
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
        mock_get_weather_data.return_value = mock_weather_data

        response = self.client.get(reverse('weather-current') + '?district=서울')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Decode and parse the JSON response
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['district'], '서울')