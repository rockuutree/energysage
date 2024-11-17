# solar/models.py

from django.db import models

class SolarInstallation(models.Model):
    case_id = models.IntegerField(primary_key=True)
    state = models.CharField(max_length=2)
    county = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    name = models.CharField(max_length=255)
    year = models.IntegerField()
    capacity_ac = models.FloatField()
    capacity_dc = models.FloatField()
    tech_primary = models.CharField(max_length=50)
    area = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['year']),
            models.Index(fields=['capacity_ac']),
        ]
        
    def __str__(self):
        return f"{self.name} - {self.state}"