from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
import requests

OPENDATA_URL = 'https://opendata.paris.fr/explore/dataset/arrondissements/download/?format=geojson&timezone=Europe/Paris'
QUARTIERS_GEOJSON_URL = 'https://opendata.paris.fr/explore/dataset/quartier_paris/download/?format=geojson&timezone=Europe/Paris'
DEPARTEMENTS_GEOJSON_URL = 'https://france-geojson.gregoiredavid.fr/repo/departements.geojson'


@require_GET
def arrondissements_geojson(request):
    try:
        r = requests.get(OPENDATA_URL, timeout=15)
        r.raise_for_status()
        resp = HttpResponse(r.content, content_type='application/geo+json')
        resp['Cache-Control'] = 'no-store'
        return resp
    except requests.RequestException as exc:
        return JsonResponse({'error': 'opendata_fetch_failed', 'detail': str(exc)}, status=502)


@require_GET
def quartiers_geojson(request):
    try:
        r = requests.get(QUARTIERS_GEOJSON_URL, timeout=15)
        r.raise_for_status()
        resp = HttpResponse(r.content, content_type='application/geo+json')
        resp['Cache-Control'] = 'no-store'
        return resp
    except requests.RequestException as exc:
        return JsonResponse({'error': 'quartiers_fetch_failed', 'detail': str(exc)}, status=502)


@require_GET
def departements_geojson(request):
    try:
        r = requests.get(DEPARTEMENTS_GEOJSON_URL, timeout=20)
        r.raise_for_status()
        resp = HttpResponse(r.content, content_type='application/geo+json')
        resp['Cache-Control'] = 'no-store'
        return resp
    except requests.RequestException as exc:
        return JsonResponse({'error': 'departements_fetch_failed', 'detail': str(exc)}, status=502) 