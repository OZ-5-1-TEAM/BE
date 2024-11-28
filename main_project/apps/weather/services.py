from typing import Dict, Any, Tuple
from datetime import datetime, time
import requests
from django.conf import settings
from .models import WeatherData, WalkingCondition

class WeatherService:
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = "http://api.waqi.info/feed/"

    def get_weather_data(self, district: str, neighborhood: str) -> Dict[str, Any]:
        location = f"{district}-{neighborhood}"
        url = f"{self.base_url}{location}/?token={self.api_key}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'ok':
                raise Exception(f"API Error: {data.get('data')}")

            weather_data = self._process_weather_data(data['data'], district, neighborhood)
            return self._save_weather_data(weather_data)

        except requests.RequestException as e:
            raise Exception(f"Weather API Request Error: {str(e)}")
        except Exception as e:
            raise Exception(f"Weather API Error: {str(e)}")

    def _process_weather_data(self, data: Dict, district: str) -> Dict:
        iaqi = data.get('iaqi', {})
        
        processed_data = {
            'district': district,
            'aqi': data.get('aqi'),
            'temperature': iaqi.get('t', {}).get('v'),
            'humidity': iaqi.get('h', {}).get('v'),
            'wind_speed': iaqi.get('w', {}).get('v'),
            'pm10': iaqi.get('pm10', {}).get('v'),
            'pm25': iaqi.get('pm25', {}).get('v'),
            'precipitation': 0.0,  # API에서 제공하지 않는 값
            'precipitation_type': None,  # API에서 제공하지 않는 값
            'forecast_time': datetime.now(),
            'walking_score': 0  # 초기값
        }
        
        processed_data['walking_score'] = self._calculate_walking_score(processed_data)
        return processed_data

    def _calculate_walking_score(self, data: Dict) -> int:
        score = 100

        # AQI 기반 점수 조정
        if data['aqi']:
            if data['aqi'] > 300:
                score -= 50
            elif data['aqi'] > 200:
                score -= 40
            elif data['aqi'] > 150:
                score -= 30
            elif data['aqi'] > 100:
                score -= 20
            elif data['aqi'] > 50:
                score -= 10

        # 온도 기반 점수 조정
        if data['temperature']:
            if data['temperature'] < 5 or data['temperature'] > 35:
                score -= 30
            elif data['temperature'] < 10 or data['temperature'] > 30:
                score -= 20
            elif data['temperature'] < 15 or data['temperature'] > 25:
                score -= 10

        # 미세먼지 기반 점수 조정
        if data['pm25']:
            if data['pm25'] > 150:
                score -= 20
            elif data['pm25'] > 100:
                score -= 15
            elif data['pm25'] > 50:
                score -= 10

        return max(0, min(score, 100))

    def _generate_walking_recommendations(self, weather_data: WeatherData) -> Tuple[str, str]:
        aqi = weather_data.aqi
        warning = None
        recommendation = "산책하기 좋은 날씨입니다."

        if aqi > 300:
            warning = "매우 위험한 대기질. 외출을 피해주세요."
            recommendation = "실내 활동을 추천드립니다."
        elif aqi > 200:
            warning = "매우 나쁜 대기질. 외출을 자제해주세요."
            recommendation = "실내 산책을 추천드립니다."
        elif aqi > 150:
            warning = "나쁜 대기질. 민감군은 외출을 피해주세요."
            recommendation = "짧은 산책만 추천드립니다."
        elif aqi > 100:
            warning = "민감군 주의. 장시간 실외 활동을 피해주세요."
            recommendation = "산책 시간을 30분 이내로 제한하세요."

        return recommendation, warning

    def _calculate_best_walking_times(self, weather_data: WeatherData) -> Dict[str, time]:
        # 일반적으로 대기질이 좋은 시간대 추천
        return {
            'start': time(6, 0),  # 오전 6시
            'end': time(9, 0)     # 오전 9시
        }

    def _save_weather_data(self, data: Dict) -> WeatherData:
        weather_data = WeatherData.objects.create(**data)
        self._create_walking_condition(weather_data)
        return weather_data