# solar/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count
from .models import SolarInstallation

@api_view(['GET'])
def state_solar_stats(request):
    """Get aggregated solar statistics by state"""
    stats = SolarInstallation.objects.values('state').annotate(
        total_capacity_ac=Sum('capacity_ac'),
        total_capacity_dc=Sum('capacity_dc'),
        installation_count=Count('case_id'),
        avg_capacity=Avg('capacity_ac'),
        total_area=Sum('area')
    ).order_by('state')
    
    return Response(list(stats))

@api_view(['GET'])
def state_detail(request, state_code):
    """Get detailed information for a specific state"""
    queryset = SolarInstallation.objects.filter(state=state_code.upper())
    
    # Get yearly progression
    yearly_stats = queryset.values('year').annotate(
        total_capacity=Sum('capacity_ac'),
        installation_count=Count('case_id')
    ).order_by('year')
    
    # Get technology distribution
    tech_distribution = queryset.values('tech_primary').annotate(
        count=Count('case_id'),
        total_capacity=Sum('capacity_ac')
    ).order_by('-count')
    
    response_data = {
        'state': state_code.upper(),
        'total_capacity': queryset.aggregate(Sum('capacity_ac'))['capacity_ac__sum'],
        'total_installations': queryset.count(),
        'yearly_progression': list(yearly_stats),
        'tech_distribution': list(tech_distribution),
        'installations': list(queryset.values(
            'name', 'year', 'capacity_ac', 'latitude', 'longitude'
        ))
    }
    
    return Response(response_data)

@api_view(['GET'])
def installation_list(request):
    """Get list of installations with filtering"""
    queryset = SolarInstallation.objects.all()
    
    # Apply filters
    state = request.GET.get('state')
    year = request.GET.get('year')
    min_capacity = request.GET.get('min_capacity')
    
    if state:
        queryset = queryset.filter(state=state.upper())
    if year:
        queryset = queryset.filter(year=int(year))
    if min_capacity:
        queryset = queryset.filter(capacity_ac__gte=float(min_capacity))
    
    data = queryset.values(
        'case_id', 'name', 'state', 'county', 
        'latitude', 'longitude', 'capacity_ac', 'year'
    )
    
    return Response(list(data))