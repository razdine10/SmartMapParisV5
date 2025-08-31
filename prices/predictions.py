from django.db.models import Avg
from .models import Year, PriceStat, DeptPriceStat, Arrondissement


def predict_paris_prices_2025():
    """Simple prediction of Paris 2025 prices based on linear trend"""
    
    # Get Paris historical data
    historical_data = []
    for year in Year.objects.all().order_by('value'):
        stats = PriceStat.objects.filter(year=year)
        if stats.exists():
            avg_price = stats.aggregate(avg=Avg('avg_price_m2'))['avg']
            if avg_price:
                historical_data.append({
                    'year': year.value,
                    'avg_price': round(avg_price)
                })
    
    if len(historical_data) < 2:
        return None
    
    # Simple trend calculation (basic linear regression)
    # Beginner formula: if it rises by X€ per year, in 2025 it will be Y€
    
    first_year = historical_data[0]
    last_year = historical_data[-1]
    
    # Average growth per year
    years_diff = last_year['year'] - first_year['year']
    price_diff = last_year['avg_price'] - first_year['avg_price']
    
    if years_diff > 0:
        annual_growth = price_diff / years_diff
        years_to_2025 = 2025 - last_year['year']
        predicted_2025 = last_year['avg_price'] + (annual_growth * years_to_2025)
        
        # Calculate growth percentage
        growth_percent = ((predicted_2025 - last_year['avg_price']) / last_year['avg_price']) * 100
        
        return {
            'predicted_price_2025': round(predicted_2025),
            'last_known_price': last_year['avg_price'],
            'last_known_year': last_year['year'],
            'annual_growth': round(annual_growth),
            'growth_percent_2025': round(growth_percent, 1),
            'historical_data': historical_data
        }
    
    return None


def predict_france_prices_2025():
    """Simple prediction of France 2025 prices based on linear trend"""
    
    # Get France historical data
    historical_data = []
    for year in Year.objects.all().order_by('value'):
        stats = DeptPriceStat.objects.filter(year=year)
        if stats.exists():
            avg_price = stats.aggregate(avg=Avg('avg_price_m2'))['avg']
            if avg_price:
                historical_data.append({
                    'year': year.value,
                    'avg_price': round(avg_price)
                })
    
    if len(historical_data) < 2:
        return None
    
    # Simple linear trend calculation
    first_year = historical_data[0]
    last_year = historical_data[-1]
    
    years_diff = last_year['year'] - first_year['year']
    price_diff = last_year['avg_price'] - first_year['avg_price']
    
    if years_diff > 0:
        annual_growth = price_diff / years_diff
        years_to_2025 = 2025 - last_year['year']
        predicted_2025 = last_year['avg_price'] + (annual_growth * years_to_2025)
        
        growth_percent = ((predicted_2025 - last_year['avg_price']) / last_year['avg_price']) * 100
        
        return {
            'predicted_price_2025': round(predicted_2025),
            'last_known_price': last_year['avg_price'],
            'last_known_year': last_year['year'],
            'annual_growth': round(annual_growth),
            'growth_percent_2025': round(growth_percent, 1),
            'historical_data': historical_data
        }
    
    return None


def predict_arrondissement_rankings_2025():
    """Predict 2025 arrondissement rankings based on individual trends"""
    
    year_2024 = Year.objects.filter(value=2024).first()
    if not year_2024:
        return []
    
    predictions = []
    
    # Get data for each arrondissement
    for arr in Arrondissement.objects.all():
        arr_stats = []
        for year in Year.objects.all().order_by('value'):
            stat = PriceStat.objects.filter(year=year, arrondissement=arr).first()
            if stat:
                arr_stats.append({
                    'year': year.value,
                    'price': stat.avg_price_m2
                })
        
        if len(arr_stats) >= 2:
            # Simple linear prediction for this arrondissement
            first = arr_stats[0]
            last = arr_stats[-1]
            
            years_diff = last['year'] - first['year']
            price_diff = last['price'] - first['price']
            
            if years_diff > 0:
                annual_growth = price_diff / years_diff
                years_to_2025 = 2025 - last['year']
                predicted_2025 = last['price'] + (annual_growth * years_to_2025)
                
                growth_percent = ((predicted_2025 - last['price']) / last['price']) * 100
                
                predictions.append({
                    'arrondissement': arr.name,
                    'code': arr.code_insee,
                    'predicted_price_2025': round(predicted_2025),
                    'current_price_2024': last['price'],
                    'annual_growth': round(annual_growth),
                    'growth_percent': round(growth_percent, 1),
                    'historical_data': arr_stats
                })
    
    # Sort by predicted price (highest first)
    predictions.sort(key=lambda x: x['predicted_price_2025'], reverse=True)
    
    return predictions[:10]  # Top 10


def generate_prediction_insights():
    """Generate comprehensive prediction insights for 2025"""
    
    # Get individual predictions
    paris_pred = predict_paris_prices_2025()
    france_pred = predict_france_prices_2025()
    arr_rankings = predict_arrondissement_rankings_2025()
    
    # Generate insights text
    insights = []
    
    if paris_pred:
        direction = "↗️" if paris_pred['growth_percent_2025'] > 0 else "↘️"
        insights.append(f"{direction} Paris 2025: {paris_pred['predicted_price_2025']:,} €/m² ({paris_pred['growth_percent_2025']:+.1f}%)")
    
    if france_pred:
        direction = "↗️" if france_pred['growth_percent_2025'] > 0 else "↘️"
        insights.append(f"{direction} France 2025: {france_pred['predicted_price_2025']:,} €/m² ({france_pred['growth_percent_2025']:+.1f}%)")
    
    if arr_rankings:
        top_arr = arr_rankings[0]
        insights.append(f"🏆 Most expensive 2025: {top_arr['arrondissement']} ({top_arr['predicted_price_2025']:,} €/m²)")
        
        # Find biggest grower
        best_growth = max(arr_rankings, key=lambda x: x['growth_percent'])
        if best_growth['growth_percent'] > 0:
            insights.append(f"📈 Best growth 2025: {best_growth['arrondissement']} ({best_growth['growth_percent']:+.1f}%)")
    
    # Add methodology note
    insights.append("⚠️ Simple linear trend method - actual results may vary")
    
    return {
        'insights': insights,
        'paris_prediction': paris_pred,
        'france_prediction': france_pred,
        'top_arrondissements': arr_rankings,
        'methodology': 'Linear trend analysis based on 2020-2024 historical data'
    } 