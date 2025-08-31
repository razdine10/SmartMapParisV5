from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Avg, Count, Max, Min
from django.core.management import call_command
from .models import Year, PriceStat, DeptPriceStat, Arrondissement, Department, Quartier, QuartierPriceStat


@require_GET
def list_years(request):
    """Return only years that have data for Paris OR France. If none, auto-seed minimal data."""
    years_paris = Year.objects.filter(price_stats__isnull=False).values_list('value', flat=True).distinct()
    years_france = Year.objects.filter(dept_price_stats__isnull=False).values_list('value', flat=True).distinct()
    years_quartiers = Year.objects.filter(quartier_price_stats__isnull=False).values_list('value', flat=True).distinct()
    years_with_data = sorted(set(years_paris) | set(years_france) | set(years_quartiers))

    if not years_with_data:
        # As a safety net in production, seed France department data
        try:
            call_command('import_all_france_departments', verbosity=0)
        except Exception:
            pass
        years_france = Year.objects.filter(dept_price_stats__isnull=False).values_list('value', flat=True).distinct()
        years_with_data = sorted(set(years_paris) | set(years_france) | set(years_quartiers))

    return JsonResponse({'years': list(years_with_data)})


@require_GET
def price_stats(request):
    """Paris arrondissements price statistics"""
    year_param = request.GET.get('year')
    if not year_param:
        return JsonResponse({'error': 'year parameter required'}, status=400)
    
    try:
        year_value = int(year_param)
        year_obj = Year.objects.get(value=year_value)
    except (ValueError, Year.DoesNotExist):
        return JsonResponse({'error': 'invalid year'}, status=400)
    
    stats = PriceStat.objects.filter(year=year_obj).select_related('arrondissement')
    
    if not stats.exists():
        return JsonResponse({'data': [], 'year': year_value})
    
    # Calculate global stats for legend
    all_prices = stats.values_list('avg_price_m2', flat=True)
    min_price = min(all_prices)
    max_price = max(all_prices)
    
    data = []
    for stat in stats:
        data.append({
            'arrondissement_code': stat.arrondissement.code_insee,
            'arrondissement_name': stat.arrondissement.name,
            'avg_price_m2': stat.avg_price_m2,
            'transaction_count': stat.transaction_count,
        })
    
    return JsonResponse({
        'data': data,
        'year': year_value,
        'legend': {
            'min_price': min_price,
            'max_price': max_price,
        }
    })


@require_GET
def quartier_price_stats(request):
    """Paris quartiers price statistics"""
    year_param = request.GET.get('year')
    if not year_param:
        return JsonResponse({'error': 'year parameter required'}, status=400)
    
    try:
        year_value = int(year_param)
        year_obj = Year.objects.get(value=year_value)
    except (ValueError, Year.DoesNotExist):
        return JsonResponse({'error': 'invalid year'}, status=400)
    
    stats = QuartierPriceStat.objects.filter(year=year_obj).select_related('quartier', 'quartier__arrondissement')
    
    if not stats.exists():
        return JsonResponse({'data': [], 'year': year_value})
    
    # Calculate global stats for legend
    all_prices = stats.values_list('avg_price_m2', flat=True)
    min_price = min(all_prices)
    max_price = max(all_prices)
    
    data = []
    for stat in stats:
        data.append({
            'quartier_code': stat.quartier.code,
            'quartier_name': stat.quartier.name,
            'arrondissement_name': stat.quartier.arrondissement.name,
            'full_name': f"{stat.quartier.name} – {stat.quartier.arrondissement.name}",
            'avg_price_m2': stat.avg_price_m2,
            'transaction_count': stat.transaction_count,
        })
    
    return JsonResponse({
        'data': data,
        'year': year_value,
        'legend': {
            'min_price': min_price,
            'max_price': max_price,
        }
    })


@require_GET
def france_dept_prices(request):
    """France departments price statistics"""
    year_param = request.GET.get('year')
    if not year_param:
        return JsonResponse({'error': 'year parameter required'}, status=400)
    
    try:
        year_value = int(year_param)
        year_obj = Year.objects.get(value=year_value)
    except (ValueError, Year.DoesNotExist):
        return JsonResponse({'error': 'invalid year'}, status=400)
    
    stats = DeptPriceStat.objects.filter(year=year_obj).select_related('department')
    
    if not stats.exists():
        return JsonResponse({'data': [], 'year': year_value})
    
    # Calculate global stats for legend
    all_prices = stats.values_list('avg_price_m2', flat=True)
    min_price = min(all_prices)
    max_price = max(all_prices)
    
    data = []
    for stat in stats:
        data.append({
            'department_code': stat.department.code,
            'department_name': stat.department.name,
            'avg_price_m2': stat.avg_price_m2,
            'transaction_count': stat.transaction_count,
        })
    
    return JsonResponse({
        'data': data,
        'year': year_value,
        'legend': {
            'min_price': min_price,
            'max_price': max_price,
        }
    }) 