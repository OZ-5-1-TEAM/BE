from django.test import TestCase
from weathers.models import WeatherData
from weathers.services import WeatherService
from unittest.mock import patch

class WeatherServiceTest(TestCase):

    @patch('weathers.services.requests.get')
    def test_get_weather_data_success(self, mock_get):
        # Mocking the API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'main': {'temp': 25.0, 'humidity': 60},
            'wind': {'speed': 5.0},
            'rain': {'1h': 0},
            'dt': 1609459200  # Example timestamp
        }

        service = WeatherService()
        weather_data = service.get_weather_data('서울')

        self.assertEqual(weather_data['district'], '서울')
        self.assertEqual(weather_data['temperature'], 25.0)
        self.assertEqual(weather_data['humidity'], 60.0)

    @patch('weathers.services.requests.get')
    def test_get_weather_data_failure(self, mock_get):
        # Mocking a failed API response
        mock_get.return_value.status_code = 404

        service = WeatherService()

        with self.assertRaises(Exception) as context:
            service.get_weather_data('서울')

        self.assertTrue('Weather API Request Error' in str(context.exception))