from django.db import models

class WeatherData(models.Model):
    district = models.CharField(max_length=50)
    neighborhood = models.CharField(max_length=50)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    precipitation = models.FloatField(null=True, blank=True, default=0.0)
    precipitation_type = models.CharField(max_length=20, null=True, blank=True)
    walking_score = models.IntegerField(default=0)
    forecast_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'weather_data'
        indexes = [
            models.Index(fields=['district', 'neighborhood']),
            models.Index(fields=['forecast_time']),
        ]
        unique_together = ('district', 'neighborhood', 'forecast_time')

    def __str__(self):
        return f"{self.district} - {self.neighborhood} - {self.forecast_time}"

class WalkingCondition(models.Model):
    weather_data = models.OneToOneField(
        WeatherData, 
        on_delete=models.CASCADE, 
        related_name='walking_condition'
    )
    recommendation = models.CharField(max_length=200)
    warning = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'walking_conditions'
        
    def __str__(self):
        return f"Walking Condition for {self.weather_data}"