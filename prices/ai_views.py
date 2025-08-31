import json
import os
import ollama
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count
from .models import Year, PriceStat, DeptPriceStat, Arrondissement, Department
from .predictions import generate_prediction_insights


# Configure Ollama base URL (works locally and in production if a remote Ollama is provided)
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL') or os.getenv('OLLAMA_HOST') or 'http://127.0.0.1:11434'
ollama_client = ollama.Client(host=OLLAMA_BASE_URL)


def get_data_context():
    """Retrieve a summary of DVF data for AI context"""
    
    # Paris statistics
    paris_stats = []
    for year in Year.objects.all().order_by('value'):
        stats = PriceStat.objects.filter(year=year)
        if stats.exists():
            avg_price = stats.aggregate(avg=Avg('avg_price_m2'))['avg']
            total_transactions = stats.aggregate(total=Count('transaction_count'))['total']
            paris_stats.append({
                'year': year.value,
                'avg_price_m2': round(avg_price or 0),
                'arrondissements_count': stats.count(),
                'total_transactions': total_transactions or 0
            })
    
    # France statistics
    france_stats = []
    for year in Year.objects.all().order_by('value'):
        stats = DeptPriceStat.objects.filter(year=year)
        if stats.exists():
            avg_price = stats.aggregate(avg=Avg('avg_price_m2'))['avg']
            total_transactions = stats.aggregate(total=Count('transaction_count'))['total']
            france_stats.append({
                'year': year.value,
                'avg_price_m2': round(avg_price or 0),
                'departments_count': stats.count(),
                'total_transactions': total_transactions or 0
            })
    
    # Top/Bottom Paris arrondissements 2024
    year_2024 = Year.objects.filter(value=2024).first()
    top_paris = []
    if year_2024:
        top_stats = PriceStat.objects.filter(year=year_2024).order_by('-avg_price_m2')[:5]
        for stat in top_stats:
            top_paris.append({
                'arrondissement': stat.arrondissement.name,
                'code': stat.arrondissement.code_insee,
                'price_m2': stat.avg_price_m2,
                'transactions': stat.transaction_count
            })
    
    return {
        'paris_evolution': paris_stats,
        'france_evolution': france_stats,
        'top_paris_2024': top_paris,
        'years_available': [y.value for y in Year.objects.all().order_by('value')]
    }


def analyze_question(question, data_context, language='fr'):
    """Analyze question with local AI and return insights + map actions"""
    
    # Add predictions to context if available
    predictions_context = ""
    prediction_keywords = ['2025', 'prédiction', 'prédire', 'futur', 'prévoir'] if language == 'fr' else ['2025', 'prediction', 'predict', 'future', 'forecast']
    if any(word in question.lower() for word in prediction_keywords):
        try:
            predictions = generate_prediction_insights()
            pred_title = "PRÉDICTIONS 2025 (méthode débutant - tendance linéaire)" if language == 'fr' else "2025 PREDICTIONS (beginner method - linear trend)"
            predictions_context = f"\n\n{pred_title}:\n{json.dumps(predictions, indent=2, ensure_ascii=False)}"
        except Exception:
            predictions_context = ""

    # AI prompt based on language
    if language == 'fr':
        system_prompt = f"""Tu es un expert en analyse immobilière française. 
Tu as accès aux données DVF (Demandes de Valeurs Foncières) de 2020 à 2024 pour Paris et toute la France.

DONNÉES DISPONIBLES:
- Paris: {len(data_context['paris_evolution'])} années de données par arrondissement
- France: {len(data_context['france_evolution'])} années de données par département  
- Évolution des prix moyens/m² de 2020 à 2024
- Nombre de transactions par zone

CONTEXTE DES DONNÉES:
{json.dumps(data_context, indent=2, ensure_ascii=False)}{predictions_context}

INSTRUCTIONS:
1. Réponds UNIQUEMENT en français
2. Sois précis avec les chiffres des données
3. Reste factuel et base-toi sur les vraies données fournies
4. Si on te demande des prédictions 2025, utilise les prédictions fournies et explique que c'est une méthode simple (tendance linéaire)

QUESTION DE L'UTILISATEUR: {question}"""
    else:
        system_prompt = f"""You are a French real estate analysis expert.
You have access to DVF (Property Value Requests) data from 2020 to 2024 for Paris and all of France.

AVAILABLE DATA:
- Paris: {len(data_context['paris_evolution'])} years of data by arrondissement
- France: {len(data_context['france_evolution'])} years of data by department
- Average price/m² evolution from 2020 to 2024
- Number of transactions per area

DATA CONTEXT:
{json.dumps(data_context, indent=2, ensure_ascii=False)}{predictions_context}

INSTRUCTIONS:
1. Answer ONLY in English
2. Be precise with data figures
3. Stay factual and base answers on the real provided data
4. If asked about 2025 predictions, use the provided predictions and explain it's a simple method (linear trend)

USER QUESTION: {question}"""

    # Call to Ollama (local or remote). If unreachable, raise explicit error.
    try:
        response = ollama_client.chat(model='llama3.2', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': question}
        ])
        return response['message']['content']
    except Exception as e:
        raise ConnectionError(f"Ollama not reachable at {OLLAMA_BASE_URL}: {e}")


@csrf_exempt
@require_POST  
def ai_chat(request):
    """AI chat endpoint for real estate analysis"""
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        language = data.get('language', 'fr')
        
        if not question:
            return JsonResponse({'error': 'question required'}, status=400)
        
        data_context = get_data_context()
        
        try:
            ai_response = analyze_question(question, data_context, language)
        except ConnectionError as ce:
            return JsonResponse({'error': 'ollama_unavailable', 'details': str(ce)}, status=503)
        
        # Check if predictions are requested
        predictions = None
        if any(word in question.lower() for word in ['2025', 'prédiction', 'predictions', 'prédire', 'futur', 'prévoir', 'forecast']):
            try:
                preds = generate_prediction_insights()
                if preds and 'insights' in preds:
                    summary_lines = []
                    for insight in preds['insights'][:3]:
                        summary_lines.append(f"• {insight}")
                    ai_response = ai_response + "\n\n" + ("Résumé prédictions 2025:\n" if language=='fr' else "2025 predictions summary:\n") + "\n".join(summary_lines)
                else:
                    predictions = preds
            except Exception:
                pass
        
        return JsonResponse({
            'response': ai_response,
            'predictions': predictions,
            'data_context': data_context
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@csrf_exempt
def ai_predictions_2025(request):
    """Generate 2025 price predictions endpoint"""
    try:
        predictions = generate_prediction_insights()
        return JsonResponse(predictions)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 