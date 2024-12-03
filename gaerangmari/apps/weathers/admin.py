from django.contrib import admin
from .models import WeatherData

class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('district', 'neighborhood', 'temperature', 'humidity', 'wind_speed', 'forecast_time')
    search_fields = ('district', 'neighborhood')
    list_filter = ('district',)

admin.site.register(WeatherData, WeatherDataAdmin)