# solar/serializers.py

from rest_framework import serializers
from .models import SolarInstallation

class SolarInstallationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolarInstallation
        fields = '__all__'

class StateSummarySerializer(serializers.Serializer):
    state = serializers.CharField()
    total_capacity_ac = serializers.FloatField()
    total_capacity_dc = serializers.FloatField()
    installation_count = serializers.IntegerField()
    avg_capacity = serializers.FloatField()
    total_area = serializers.FloatField()
    latest_year = serializers.IntegerField()