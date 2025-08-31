import requests
import random
from django.core.management.base import BaseCommand
from prices.models import Arrondissement, Quartier, Year, QuartierPriceStat


class Command(BaseCommand):
    help = 'Populate database with Paris quartiers and sample price data'

    def handle(self, *args, **options):
        self.stdout.write('Fetching quartiers data from opendata.paris.fr...')
        
        # Fetch quartiers GeoJSON data
        try:
            response = requests.get(
                'https://opendata.paris.fr/explore/dataset/quartier_paris/download/?format=geojson&timezone=Europe/Paris',
                timeout=30
            )
            response.raise_for_status()
            geojson_data = response.json()
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch data: {e}'))
            return

        self.stdout.write('Processing quartiers data...')
        
        # Create arrondissements if they don't exist
        arr_mapping = {}
        for i in range(1, 21):
            code = f"7510{i:02d}" if i < 10 else f"751{i:02d}"
            name = f"{i}{'er' if i == 1 else 'ème'} arrondissement"
            arr, created = Arrondissement.objects.get_or_create(
                code_insee=code, 
                defaults={'name': name}
            )
            arr_mapping[i] = arr
            if created:
                self.stdout.write(f'Created arrondissement: {name}')

        # Process quartiers
        quartiers_created = 0
        quartiers_updated = 0
        
        for feature in geojson_data.get('features', []):
            props = feature.get('properties', {})
            
            # Extract quartier information
            quartier_code = props.get('c_qu')
            quartier_name = props.get('l_qu', '').strip()
            arr_number = props.get('c_ar')
            
            if not all([quartier_code, quartier_name, arr_number]):
                continue
                
            try:
                arr_number = int(arr_number)
                if arr_number not in arr_mapping:
                    continue
                    
                arrondissement = arr_mapping[arr_number]
                
                # Create or update quartier
                quartier, created = Quartier.objects.get_or_create(
                    code=str(quartier_code),
                    defaults={
                        'name': quartier_name,
                        'arrondissement': arrondissement
                    }
                )
                
                if created:
                    quartiers_created += 1
                    self.stdout.write(f'Created quartier: {quartier_name} – {arrondissement.name}')
                else:
                    quartier.name = quartier_name
                    quartier.arrondissement = arrondissement
                    quartier.save()
                    quartiers_updated += 1
                    
            except (ValueError, KeyError) as e:
                self.stdout.write(f'Error processing quartier {quartier_name}: {e}')
                continue

        self.stdout.write(f'Quartiers created: {quartiers_created}, updated: {quartiers_updated}')

        # Create sample price data for years 2020-2024
        self.stdout.write('Creating sample price data...')
        
        years = []
        for year_value in range(2020, 2025):
            year, created = Year.objects.get_or_create(value=year_value)
            years.append(year)
            if created:
                self.stdout.write(f'Created year: {year_value}')

        # Generate realistic price data for each quartier and year
        price_stats_created = 0
        
        # Base prices by arrondissement (realistic 2024 values in €/m²)
        base_prices = {
            1: 12500, 2: 11000, 3: 11500, 4: 13000, 5: 10500,
            6: 13500, 7: 14000, 8: 11500, 9: 10000, 10: 9500,
            11: 9800, 12: 9000, 13: 8800, 14: 9200, 15: 10200,
            16: 12000, 17: 9800, 18: 8500, 19: 7800, 20: 8200
        }

        for quartier in Quartier.objects.all():
            arr_num = int(quartier.arrondissement.code_insee[-2:])
            base_price = base_prices.get(arr_num, 9000)
            
            for year in years:
                # Generate price evolution from 2020 to 2024
                year_factor = 1 + (year.value - 2020) * 0.05  # 5% growth per year
                quartier_variation = random.uniform(0.85, 1.15)  # ±15% variation between quartiers
                annual_variation = random.uniform(0.95, 1.05)   # ±5% annual variation
                
                price = int(base_price * year_factor * quartier_variation * annual_variation)
                transactions = random.randint(50, 300)
                
                quartier_stat, created = QuartierPriceStat.objects.get_or_create(
                    quartier=quartier,
                    year=year,
                    defaults={
                        'avg_price_m2': price,
                        'transaction_count': transactions
                    }
                )
                
                if created:
                    price_stats_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated database:\n'
                f'- {quartiers_created} quartiers created, {quartiers_updated} updated\n'
                f'- {price_stats_created} price statistics created\n'
                f'- Years 2020-2024 available'
            )
        ) 