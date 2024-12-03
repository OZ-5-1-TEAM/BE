from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import WeatherData
from .services import WeatherService
from .serializers import WeatherDataSerializer

class WeatherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer

    @action(detail=False, methods=['get'])
    def current(self, request):
        district = request.query_params.get('district')

        if not district:
            return Response(
                {"error": "district parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            weather_service = WeatherService()
            weather_data = weather_service.get_weather_data(district)
            serializer = self.get_serializer(weather_data)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch weather data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )