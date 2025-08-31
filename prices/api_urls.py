from django.urls import path
from . import api_views
from . import opendata_views
from . import ai_views

urlpatterns = [
    path('prices/', api_views.price_stats, name='api-prices'),
    path('quartiers/prices/', api_views.quartier_price_stats, name='api-quartiers-prices'),
    path('years/', api_views.list_years, name='api-years'),
    path('arrondissements/', opendata_views.arrondissements_geojson, name='api-arrondissements'),
    path('quartiers/', opendata_views.quartiers_geojson, name='api-quartiers'),
    path('france/prices/', api_views.france_dept_prices, name='api-france-prices'),
    path('france/departements/', opendata_views.departements_geojson, name='api-france-departements'),
    path('ai/chat/', ai_views.ai_chat, name='api-ai-chat'),

    path('ai/predictions/', ai_views.ai_predictions_2025, name='api-ai-predictions'),
] 