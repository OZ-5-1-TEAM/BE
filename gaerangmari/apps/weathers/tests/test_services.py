from django.test import TestCase
from weathers.models import WeatherData
from weathers.services import WeatherService
from unittest.mock import patch
import requests

class WeatherServiceTest(TestCase):

    @patch('weathers.services.requests.get')
    def test_get_weather_data_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'main': {'temp': 25.0, 'humidity': 60},
            'wind': {'speed': 5.0},
            'rain': {'1h': 0},
            'dt': 1609459200
        }

        service = WeatherService()
        weather_data = service.get_weather_data('서울')

        self.assertEqual(weather_data.district, '서울')
        self.assertEqual(weather_data.temperature, 25.0)
        self.assertEqual(weather_data.humidity, 60.0)

    @patch('weathers.services.requests.get')
    def test_get_weather_data_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException("API Error")

        service = WeatherService()

        with self.assertRaises(Exception) as context:
            service.get_weather_data('서울')

        self.assertIn('Weather API Request Error', str(context.exception))