# solar/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('api/solar/stats/', views.state_solar_stats, name='state-solar-stats'),
    path('api/solar/state/<str:state_code>/', views.state_detail, name='state-detail'),
    path('api/solar/installations/', views.installation_list, name='installation-list'),
]