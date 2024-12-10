# weathers/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests

class CurrentWeatherView(APIView):
    def get(self, request):
        TOMORROW_API_KEY = settings.TOMORROW_API_KEY
        SEOUL_LAT = '37.5665'
        SEOUL_LON = '126.9780'
        
        url = "https://api.tomorrow.io/v4/weather/realtime"
        params = {
            'location': f'{SEOUL_LAT},{SEOUL_LON}',
            'apikey': TOMORROW_API_KEY,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # API 응답 구조 확인을 위한 로깅
            print("API Response:", data)
            
            if not response.ok:
                return Response(
                    {"error": f"API Error: {data.get('message', 'Unknown error')}"},
                    status=response.status_code
                )
            
            try:
                weather_data = {
                    'temperature': data['data']['values']['temperature'],
                    'humidity': data['data']['values']['humidity'],
                    'wind_speed': data['data']['values']['windSpeed'],
                    'precipitation_probability': data['data']['values']['precipitationProbability'],
                    'weather_code': data['data']['values']['weatherCode']
                }
            except KeyError as ke:
                return Response(
                    {"error": f"Missing expected data in API response: {str(ke)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(weather_data)
            
        except requests.RequestException as e:
            return Response(
                {"error": f"Request failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )