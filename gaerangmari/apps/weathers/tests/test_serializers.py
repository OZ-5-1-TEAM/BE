from django.test import TestCase
from weathers.models import WeatherData
from weathers.serializers import WeatherDataSerializer

class WeatherDataSerializerTest(TestCase):

    def test_valid_serializer(self):
        data = {
            'district': '서울',
            'neighborhood': '강남',
            'temperature': 25.0,
            'humidity': 60.0,
            'wind_speed': 5.0,
            'precipitation': 0.0,
            'precipitation_type': 'none',
            'walking_score': 80,
            'forecast_time': "2024-12-03T10:00:00Z"
        }
        serializer = WeatherDataSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_serializer(self):
        data = {
            'district': '',
            'neighborhood': '',
        }
        serializer = WeatherDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('district', serializer.errors)