from rest_framework import serializers
from ..models import WeatherData, WalkingCondition

class WalkingConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalkingCondition
        exclude = ('weather_data',)

class WeatherDataSerializer(serializers.ModelSerializer):
    walking_condition = WalkingConditionSerializer(read_only=True)

    class Meta:
        model = WeatherData
        fields = '__all__'