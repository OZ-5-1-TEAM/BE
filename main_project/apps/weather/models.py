from django.db import models

class WeatherData(models.Model):
    district = models.CharField(max_length=50)
    aqi = models.IntegerField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    pm10 = models.FloatField(null=True, blank=True)
    pm25 = models.FloatField(null=True, blank=True)
    precipitation = models.FloatField(null=True, blank=True, default=0.0)
    precipitation_type = models.CharField(max_length=20, null=True, blank=True)
    walking_score = models.IntegerField(default=0)
    forecast_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'weather_data'
        indexes = [
            models.Index(fields=['district']),
            models.Index(fields=['forecast_time']),
        ]
        unique_together = ('district', 'forecast_time')

    def __str__(self):
        return f"{self.district} - {self.forecast_time}"

class WalkingCondition(models.Model):
    RECOMMENDATION_CHOICES = [
        ('INDOOR', '실내 활동을 추천드립니다.'),
        ('INDOOR_WALK', '실내 산책을 추천드립니다.'),
        ('SHORT_WALK', '짧은 산책만 추천드립니다.'),
        ('LIMITED_WALK', '산책 시간을 30분 이내로 제한하세요.'),
        ('GOOD', '산책하기 좋은 날씨입니다.')
    ]

    weather_data = models.OneToOneField(
        WeatherData, 
        on_delete=models.CASCADE, 
        related_name='walking_condition'
    )
    recommendation = models.CharField(
        max_length=200,
        choices=RECOMMENDATION_CHOICES,
        default='GOOD'
    )
    warning = models.CharField(max_length=200, null=True, blank=True)
    best_time_start = models.TimeField()
    best_time_end = models.TimeField()

    class Meta:
        db_table = 'walking_conditions'
        
    def __str__(self):
        return f"Walking Condition for {self.weather_data}"