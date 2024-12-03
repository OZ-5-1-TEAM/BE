from django.test import TestCase
from weathers.models import WeatherData

class WeatherDataModelTest(TestCase):

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

    def test_weather_data_content(self):
        weather_data = WeatherData.objects.get(id=1)
        self.assertEqual(weather_data.district, "서울")
        self.assertEqual(weather_data.temperature, 25.0)