from django.test import TestCase
from weathers.services import WeatherService
import os

class WeatherServiceIntegrationTest(TestCase):
    def setUp(self):
        self.weather_service = WeatherService()
        self.test_city = "seoul"
        
    def test_real_api_weather_data(self):
        try:
            # 실제 API 호출
            weather_data = self.weather_service.get_weather_data(self.test_city)
            
            # 필수 필드 존재 확인
            self.assertIsNotNone(weather_data)
            self.assertEqual(weather_data.district, self.test_city)
            self.assertIsNotNone(weather_data.temperature)
            self.assertIsNotNone(weather_data.humidity)
            self.assertIsNotNone(weather_data.wind_speed)
            
            # 데이터 타입 검증
            self.assertIsInstance(weather_data.temperature, float)
            self.assertIsInstance(weather_data.humidity, float)
            self.assertIsInstance(weather_data.wind_speed, float)
            
            # 데이터 범위 검증
            self.assertGreater(weather_data.walking_score, 0)
            self.assertLess(weather_data.walking_score, 101)
            
            # Walking Condition 검증
            self.assertIsNotNone(weather_data.walking_condition)
            self.assertIsNotNone(weather_data.walking_condition.recommendation)
            
        except Exception as e:
            self.fail(f"API 호출 실패: {str(e)}")