from django.core.management.base import BaseCommand
from prices.models import Year, Department, DeptPriceStat
import random

# All French departments with realistic prices by region
ALL_FRANCE_DEPARTMENTS = {
    # Île-de-France (expensive)
    "75": ("Paris", 12600),
    "77": ("Seine-et-Marne", 4300),
    "78": ("Yvelines", 6200),
    "91": ("Essonne", 4600),
    "92": ("Hauts-de-Seine", 8800),
    "93": ("Seine-Saint-Denis", 4900),
    "94": ("Val-de-Marne", 5600),
    "95": ("Val-d'Oise", 5200),
    
    # Provence-Alpes-Côte d'Azur (expensive - tourism)
    "04": ("Alpes-de-Haute-Provence", 3800),
    "05": ("Hautes-Alpes", 4200),
    "06": ("Alpes-Maritimes", 7100),
    "13": ("Bouches-du-Rhône", 5200),
    "83": ("Var", 5800),
    "84": ("Vaucluse", 4100),
    
    # Auvergne-Rhône-Alpes (medium-expensive)
    "01": ("Ain", 4200),
    "03": ("Allier", 1800),
    "07": ("Ardèche", 2900),
    "15": ("Cantal", 1600),
    "26": ("Drôme", 3400),
    "38": ("Isère", 4100),
    "42": ("Loire", 2800),
    "43": ("Haute-Loire", 2200),
    "63": ("Puy-de-Dôme", 2900),
    "69": ("Rhône", 5600),
    "73": ("Savoie", 6200),
    "74": ("Haute-Savoie", 7800),
    
    # Nouvelle-Aquitaine
    "16": ("Charente", 2100),
    "17": ("Charente-Maritime", 3600),
    "19": ("Corrèze", 1900),
    "23": ("Creuse", 1200),
    "24": ("Dordogne", 2400),
    "33": ("Gironde", 5000),
    "40": ("Landes", 3200),
    "47": ("Lot-et-Garonne", 2000),
    "64": ("Pyrénées-Atlantiques", 4400),
    "79": ("Deux-Sèvres", 1900),
    "86": ("Vienne", 2100),
    "87": ("Haute-Vienne", 1800),
    
    # Occitanie
    "09": ("Ariège", 2200),
    "11": ("Aude", 2600),
    "12": ("Aveyron", 2100),
    "30": ("Gard", 3200),
    "31": ("Haute-Garonne", 4800),
    "32": ("Gers", 1900),
    "34": ("Hérault", 4500),
    "46": ("Lot", 2300),
    "48": ("Lozère", 1700),
    "65": ("Hautes-Pyrénées", 2400),
    "66": ("Pyrénées-Orientales", 3400),
    "81": ("Tarn", 2500),
    "82": ("Tarn-et-Garonne", 2200),
    
    # Bretagne
    "22": ("Côtes-d'Armor", 2800),
    "29": ("Finistère", 3000),
    "35": ("Ille-et-Vilaine", 4000),
    "56": ("Morbihan", 3200),
    
    # Pays de la Loire
    "44": ("Loire-Atlantique", 4600),
    "49": ("Maine-et-Loire", 2800),
    "53": ("Mayenne", 2000),
    "72": ("Sarthe", 2400),
    "85": ("Vendée", 3000),
    
    # Centre-Val de Loire
    "18": ("Cher", 1700),
    "28": ("Eure-et-Loir", 2600),
    "36": ("Indre", 1400),
    "37": ("Indre-et-Loire", 2900),
    "41": ("Loir-et-Cher", 2300),
    "45": ("Loiret", 2800),
    
    # Hauts-de-France
    "02": ("Aisne", 2000),
    "59": ("Nord", 3000),
    "60": ("Oise", 3400),
    "62": ("Pas-de-Calais", 2400),
    "80": ("Somme", 2200),
    
    # Grand Est
    "08": ("Ardennes", 1800),
    "10": ("Aube", 2000),
    "51": ("Marne", 2400),
    "52": ("Haute-Marne", 1600),
    "54": ("Meurthe-et-Moselle", 2600),
    "55": ("Meuse", 1500),
    "57": ("Moselle", 2800),
    "67": ("Bas-Rhin", 3800),
    "68": ("Haut-Rhin", 3200),
    "88": ("Vosges", 2000),
    
    # Bourgogne-Franche-Comté
    "21": ("Côte-d'Or", 3200),
    "25": ("Doubs", 2900),
    "39": ("Jura", 2800),
    "58": ("Nièvre", 1600),
    "70": ("Haute-Saône", 1800),
    "71": ("Saône-et-Loire", 2200),
    "89": ("Yonne", 2000),
    "90": ("Territoire de Belfort", 2600),
    
    # Normandie
    "14": ("Calvados", 3100),
    "27": ("Eure", 2800),
    "50": ("Manche", 2400),
    "61": ("Orne", 1900),
    "76": ("Seine-Maritime", 2900),
    
    # Corse
    "2A": ("Corse-du-Sud", 4800),
    "2B": ("Haute-Corse", 4200),
    
    # DOM-TOM
    "971": ("Guadeloupe", 3800),
    "972": ("Martinique", 4200),
    "973": ("Guyane", 3200),
    "974": ("La Réunion", 4000),
    "976": ("Mayotte", 2800),
}


class Command(BaseCommand):
    help = "Import data for ALL French departments"

    def handle(self, *args, **options):
        years = [2020, 2021, 2022, 2023, 2024]
        
        for year_val in years:
            year_obj, _ = Year.objects.get_or_create(value=year_val)
            
            for code, (name, base_price) in ALL_FRANCE_DEPARTMENTS.items():
                # Price variation per year (slight increase)
                year_factor = 1 + (year_val - 2020) * 0.03  # +3% per year
                # Random variation ±10%
                random_factor = random.uniform(0.9, 1.1)
                final_price = int(base_price * year_factor * random_factor)
                
                # Random but coherent number of transactions
                base_tx = max(50, int(base_price / 10))  # More expensive = more transactions
                transactions = random.randint(base_tx // 2, base_tx * 2)
                
                # Create the department
                dept_obj, _ = Department.objects.get_or_create(
                    code=code,
                    defaults={'name': name}
                )
                
                # Create/update the statistic
                DeptPriceStat.objects.update_or_create(
                    department=dept_obj,
                    year=year_obj,
                    defaults={
                        'avg_price_m2': final_price,
                        'transaction_count': transactions
                    }
                )
        
        total_depts = len(ALL_FRANCE_DEPARTMENTS)
        total_stats = total_depts * len(years)
        
        self.stdout.write(self.style.SUCCESS(
            f"Import completed! {total_depts} departments × {len(years)} years = {total_stats} statistics created"
        )) 