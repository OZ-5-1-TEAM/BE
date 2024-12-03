from typing import Dict, Any, Tuple
from datetime import datetime, time
import requests
from django.conf import settings
from .models import WeatherData, WalkingCondition

class WeatherService:
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather_data(self, district: str) -> Dict[str, Any]:
        location = f"{district}"
        url = f"{self.base_url}?q={location}&appid={self.api_key}&units=metric"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            weather_data = self._process_weather_data(data, district)
            return self._save_weather_data(weather_data)

        except requests.RequestException as e:
            raise Exception(f"Weather API Request Error: {str(e)}")
        except Exception as e:
            raise Exception(f"Weather API Error: {str(e)}")

    def _process_weather_data(self, data: Dict, district: str) -> Dict:
        processed_data = {
            'district': district,
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'precipitation': data.get('rain', {}).get('1h', 0),
            'precipitation_type': 'rain' if 'rain' in data else None,
            'forecast_time': datetime.fromtimestamp(data['dt']),
            'walking_score': 0
        }
        
        processed_data['walking_score'] = self._calculate_walking_score(processed_data)
        return processed_data

    def _calculate_walking_score(self, data: Dict) -> int:
        score = 100

        # 온도 기반 점수 조정
        if data['temperature'] < 5 or data['temperature'] > 35:
            score -= 30
        elif data['temperature'] < 10 or data['temperature'] > 30:
            score -= 20
        elif data['temperature'] < 15 or data['temperature'] > 25:
            score -= 10

        # 습도 기반 점수 조정
        if data['humidity'] > 80:
            score -= 20
        elif data['humidity'] > 60:
            score -= 10

        # 풍속 기반 점수 조정
        if data['wind_speed'] > 10:
            score -= 20
        elif data['wind_speed'] > 5:
            score -= 10

        # 강수량 기반 점수 조정
        if data['precipitation'] > 5:
            score -= 30
        elif data['precipitation'] > 1:
            score -= 20
        elif data['precipitation'] > 0:
            score -= 10

        return max(0, min(score, 100))

    def _generate_walking_recommendations(self, weather_data: WeatherData) -> Tuple[str, str]:
        warning = None
        recommendation = "산책하기 좋은 날씨입니다."

        if weather_data.temperature < 5 or weather_data.temperature > 35:
            warning = "극단적인 온도. 외출 시 주의가 필요합니다."
            recommendation = "실내 활동을 추천드립니다."
        elif weather_data.precipitation > 5:
            warning = "강한 비. 외출을 자제해주세요."
            recommendation = "실내 산책을 추천드립니다."
        elif weather_data.wind_speed > 10:
            warning = "강한 바람. 외출 시 주의가 필요합니다."
            recommendation = "짧은 산책만 추천드립니다."

        return recommendation, warning


    def _save_weather_data(self, data: Dict) -> WeatherData:
        weather_data = WeatherData.objects.create(**data)
        self._create_walking_condition(weather_data)
        return weather_data

    def _create_walking_condition(self, weather_data: WeatherData):
        recommendation, warning = self._generate_walking_recommendations(weather_data)
        
        WalkingCondition.objects.create(
            weather_data=weather_data,
            recommendation=recommendation,
            warning=warning
        )