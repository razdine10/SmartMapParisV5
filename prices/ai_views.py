import json
import os
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count
from .models import Year, PriceStat, DeptPriceStat, Arrondissement, Department
from .predictions import generate_prediction_insights


# Groq API Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'gsk_dummy_key_replace_with_real')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"  # Fast and good model


def call_groq_api(question, data_context, language='fr'):
    """Call Groq API for AI responses"""
    
    # Create system prompt
    if language == 'fr':
        system_content = f"""Tu es un expert en analyse immobilière française spécialisé dans les données DVF.
Tu as accès aux données officielles de 2020 à 2024 pour Paris et toute la France.

DONNÉES DISPONIBLES:
- Paris: {len(data_context.get('paris_evolution', []))} années de données par arrondissement
- France: {len(data_context.get('france_evolution', []))} années de données par département
- Évolution des prix moyens/m² de 2020 à 2024
- Nombre de transactions par zone

CONTEXTE DES DONNÉES:
{json.dumps(data_context, indent=2, ensure_ascii=False)}

INSTRUCTIONS:
1. Réponds UNIQUEMENT en français
2. Utilise les vraies données fournies pour tes analyses
3. Sois précis avec les chiffres
4. Donne des conseils pratiques et pertinents
5. Structure ta réponse avec des emojis et du markdown

Tu peux analyser les tendances, comparer les arrondissements, donner des conseils d'investissement basés sur les vraies données."""
    else:
        system_content = f"""You are a French real estate expert specialized in DVF data analysis.
You have access to official data from 2020 to 2024 for Paris and all of France.

AVAILABLE DATA:
- Paris: {len(data_context.get('paris_evolution', []))} years of data by arrondissement  
- France: {len(data_context.get('france_evolution', []))} years of data by department
- Average price/m² evolution from 2020 to 2024
- Number of transactions per area

DATA CONTEXT:
{json.dumps(data_context, indent=2, ensure_ascii=False)}

INSTRUCTIONS:
1. Answer ONLY in English
2. Use the real provided data for your analysis
3. Be precise with figures
4. Give practical and relevant advice
5. Structure your response with emojis and markdown

You can analyze trends, compare arrondissements, give investment advice based on real data."""

    # Prepare the API request
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": question}
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
        "stream": False
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            return "Erreur dans la réponse de l'API"
            
    except requests.exceptions.RequestException as e:
        # Fallback to simple responses if Groq fails
        return simple_ai_response(question)
    except Exception as e:
        # Fallback to simple responses if any other error
        return simple_ai_response(question)


# Fallback simple AI response system (backup if Groq fails)
def simple_ai_response(question):
    """Simple rule-based AI responses for real estate questions"""
    question_lower = question.lower()
    
    # Investment advice
    if any(word in question_lower for word in ['investir', 'investment', 'acheter', 'buy']):
        return """🏡 **Conseils d'investissement immobilier Paris 2024-2025 :**

• **Arrondissements émergents** : 19e, 20e - Prix en hausse, potentiel de plus-value
• **Secteurs stables** : 11e, 12e - Bon rapport qualité/prix
• **Zones premium** : 6e, 7e, 16e - Valeur refuge mais prix élevés

**Tendances 2024** :
- Prix moyens Paris : ~10 500 €/m²
- Hausse modérée attendue (+2-3%)
- Privilégier proximité transports

*Conseil* : Diversifiez géographiquement et vérifiez l'état du bien."""

    # Price trends
    elif any(word in question_lower for word in ['prix', 'price', 'evolution', 'trend']):
        return """📈 **Évolution des prix immobiliers :**

**Paris 2024** :
- Prix moyen : ~10 500 €/m²
- Variation : +2.1% vs 2023
- Plus cher : 1er arr. (~15 000 €/m²)
- Plus accessible : 19e, 20e (~8 000 €/m²)

**France 2024** :
- Prix moyen national : ~2 800 €/m²
- Forte disparité régionale
- Îles-de-France vs Province : x3-4

**Prédictions 2025** :
- Stabilisation attendue
- Hausse modérée (+1-3%)"""

    # Best neighborhoods
    elif any(word in question_lower for word in ['quartier', 'arrondissement', 'neighborhood', 'où']):
        return """🗺️ **Meilleurs quartiers Paris 2024 :**

**Pour investir** :
• **19e** - Belleville, Buttes Chaumont
• **20e** - Gambetta, Père Lachaise  
• **12e** - Bastille, Nation

**Pour habiter** :
• **11e** - République, Oberkampf
• **10e** - Canal Saint-Martin
• **15e** - Montparnasse

**Critères importants** :
- Proximité métro/RER
- Commerces et écoles
- Projets d'aménagement
- Sécurité du quartier"""

    # General market
    elif any(word in question_lower for word in ['marché', 'market', 'immobilier', 'real estate']):
        return """🏢 **Marché immobilier France 2024 :**

**Tendances générales** :
- Légère baisse des transactions (-5%)
- Taux d'intérêt stabilisés (~4%)
- Demande concentrée sur l'ancien

**Paris spécifiquement** :
- Marché tendu, offre limitée
- Forte demande locative
- Rendements : 3-4% brut

**Conseils actuels** :
- Négocier les prix
- Privilégier l'emplacement
- Anticiper les travaux énergétiques"""

    # Default response
    else:
        return """🤖 **Assistant Immobilier SmartMapParis**

Je peux vous aider sur :
• **Investissement** : Où et comment investir
• **Prix** : Évolutions et prédictions
• **Quartiers** : Analyse par zone
• **Marché** : Tendances générales

*Posez-moi une question spécifique sur l'immobilier parisien !*

Exemples :
- "Où investir à Paris en 2024 ?"
- "Évolution des prix dans le 11e ?"
- "Meilleurs quartiers pour acheter ?"
"""


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
    """Analyze question with Groq AI and return insights"""
    
    # Use Groq API for intelligent responses
    return call_groq_api(question, data_context, language)


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
        
        ai_response = call_groq_api(question, data_context, language)
        
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