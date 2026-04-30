# environmental_pricing.py - Module de calcul de prix avec facteurs environnementaux
import datetime
import requests
from kivy.clock import Clock

class EnvironmentalPricing:
    """
    Module pour calculer les prix en fonction des facteurs environnementaux:
    - Heure de la journée (nuit, heure de pointe)
    - Météo (pluie, tempête) via OpenWeatherMap
    - Distance réelle
    - Catégorie de service
    """
    
    # Tarifs de base par catégorie (KMF) - ADAPTÉS AU MARCHÉ LOCAL
    BASE_TARIFFS = {
        'standard': {'base': 400, 'per_km': 250},
        'confort': {'base': 500, 'per_km': 300},
        'luxe': {'base': 600, 'per_km': 400},
        'moto': {'base': 250, 'per_km': 150}
    }
    
    # Multiplicateurs selon l'heure
    TIME_MULTIPLIERS = {
        'night': 1.3,      # 22h-6h
        'peak': 1.4,       # 7h-9h, 17h-19h
        'weekend': 1.2,    # Samedi, Dimanche
        'normal': 1.0      # Autres heures
    }
    
    # Multiplicateurs selon la météo
    WEATHER_MULTIPLIERS = {
        'thunderstorm': 1.6,  # Orage
        'heavy_rain': 1.5,    # Pluie forte
        'rain': 1.3,          # Pluie
        'drizzle': 1.2,       # Bruine
        'fog': 1.2,           # Brouillard
        'normal': 1.0         # Normal
    }
    
    # Cache météo pour éviter trop d'appels API (valide 30 minutes)
    _weather_cache = {}
    _cache_duration = 1800  # 30 minutes en secondes
    
    @staticmethod
    def get_current_time_factor():
        """Déterminer le facteur horaire actuel"""
        now = datetime.datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0 = Lundi, 6 = Dimanche
        
        # Heures de nuit (22h-6h)
        if 22 <= hour or hour < 6:
            return EnvironmentalPricing.TIME_MULTIPLIERS['night']
        
        # Heures de pointe (7h-9h, 17h-19h)
        elif (7 <= hour < 9) or (17 <= hour < 19):
            return EnvironmentalPricing.TIME_MULTIPLIERS['peak']
        
        # Week-end
        elif weekday >= 5:  # Samedi (5) ou Dimanche (6)
            return EnvironmentalPricing.TIME_MULTIPLIERS['weekend']
        
        # Heure normale
        else:
            return EnvironmentalPricing.TIME_MULTIPLIERS['normal']
    
    @staticmethod
    def get_weather_data(lat, lng):
        """
        Récupérer les données météo via OpenWeatherMap
        GRATUIT : 1 000 000 appels/mois
        """
        # Vérifier le cache d'abord
        import time
        cache_key = f"{round(lat, 2)}_{round(lng, 2)}"
        
        if cache_key in EnvironmentalPricing._weather_cache:
            cached_data, timestamp = EnvironmentalPricing._weather_cache[cache_key]
            if time.time() - timestamp < EnvironmentalPricing._cache_duration:
                print(f"🌤️ Météo depuis cache: {cached_data['weather_desc']}")
                return cached_data
        
        try:
            # Importer la clé API depuis la config
            import sys
            import os.path as osp
            sys.path.append(osp.dirname(osp.abspath(__file__)))
            from config.config import Config
            OPENWEATHER_API_KEY = Config.OPENWEATHER_API_KEY
            
            # Coordonnées par défaut (Moroni)
            if lat is None or lng is None:
                lat = -11.6980
                lng = 43.2560
            
            # URL de l'API OpenWeatherMap
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': lat,
                'lon': lng,
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric',
                'lang': 'fr'
            }
            
            print(f"🌤️ Appel OpenWeatherMap: ({lat:.4f}, {lng:.4f})")
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraire les données
                weather = data.get('weather', [{}])[0]
                main = data.get('main', {})
                
                weather_main = weather.get('main', 'normal').lower()
                weather_desc = weather.get('description', 'conditions normales')
                temp = main.get('temp', 25)
                humidity = main.get('humidity', 70)
                
                result = {
                    'success': True,
                    'weather_main': weather_main,
                    'weather_desc': weather_desc,
                    'temperature': temp,
                    'humidity': humidity,
                    'source': 'OpenWeatherMap'
                }
                
                # Stocker dans le cache
                EnvironmentalPricing._weather_cache[cache_key] = (result, time.time())
                
                print(f"   ✅ {weather_desc}, {temp:.0f}°C")
                return result
                
            elif response.status_code == 401:
                print(f"⚠️ OpenWeatherMap: Clé API invalide ou non activée")
            elif response.status_code == 429:
                print(f"⚠️ OpenWeatherMap: Limite d'appels dépassée")
            else:
                print(f"⚠️ OpenWeatherMap error: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Erreur OpenWeatherMap: {e}")
        
        # Fallback : conditions normales
        return {
            'success': False,
            'weather_main': 'normal',
            'weather_desc': 'conditions normales',
            'temperature': 25,
            'source': 'fallback'
        }
    
    @staticmethod
    def get_weather_factor(lat=None, lng=None):
        """Déterminer le facteur météo"""
        weather_data = EnvironmentalPricing.get_weather_data(lat, lng)
        
        weather_main = weather_data.get('weather_main', 'normal')
        
        # Mapper les conditions météo aux multiplicateurs
        if 'thunderstorm' in weather_main:
            return EnvironmentalPricing.WEATHER_MULTIPLIERS['thunderstorm']
        elif 'rain' in weather_main:
            # Vérifier si pluie forte (intensité)
            if 'heavy' in weather_data.get('weather_desc', '') or 'forte' in weather_data.get('weather_desc', ''):
                return EnvironmentalPricing.WEATHER_MULTIPLIERS['heavy_rain']
            return EnvironmentalPricing.WEATHER_MULTIPLIERS['rain']
        elif 'drizzle' in weather_main:
            return EnvironmentalPricing.WEATHER_MULTIPLIERS['drizzle']
        elif 'fog' in weather_main or 'mist' in weather_main:
            return EnvironmentalPricing.WEATHER_MULTIPLIERS['fog']
        else:
            return EnvironmentalPricing.WEATHER_MULTIPLIERS['normal']
    
    @staticmethod
    def calculate_price(distance_km, service_category, lat=None, lng=None):
        """
        Calculer le prix final avec tous les facteurs environnementaux
        """
        # Vérifier la catégorie
        if service_category not in EnvironmentalPricing.BASE_TARIFFS:
            service_category = 'standard'
        
        # Récupérer les tarifs de base
        base_tariff = EnvironmentalPricing.BASE_TARIFFS[service_category]
        base_price = base_tariff['base']
        per_km = base_tariff['per_km']
        
        # Calcul du prix de base
        base_calculation = base_price + (distance_km * per_km)
        
        # Appliquer les facteurs environnementaux
        time_factor = EnvironmentalPricing.get_current_time_factor()
        weather_factor = EnvironmentalPricing.get_weather_factor(lat, lng)
        
        # Calcul du prix final
        final_price = base_calculation * time_factor * weather_factor
        
        # Arrondir à la centaine supérieure
        final_price = ((final_price + 99) // 100) * 100
        
        # Prix minimum garanti (base × 1.2)
        min_price = base_price * 1.2
        if final_price < min_price:
            final_price = ((min_price + 99) // 100) * 100
        
        # Informations de débug
        print(f"💰 Calcul prix {service_category}:")
        print(f"   - Distance: {distance_km:.2f} km")
        print(f"   - Base: {base_price} + ({distance_km:.2f} × {per_km}) = {base_calculation:.0f}")
        print(f"   - Facteur heure: {time_factor:.2f}")
        print(f"   - Facteur météo: {weather_factor:.2f}")
        print(f"   - Prix final: {final_price:.0f} KMF")
        
        return int(final_price)
    
    @staticmethod
    def get_price_breakdown(distance_km, service_category, lat=None, lng=None):
        """Obtenir une décomposition détaillée du prix"""
        if service_category not in EnvironmentalPricing.BASE_TARIFFS:
            service_category = 'standard'
        
        base_tariff = EnvironmentalPricing.BASE_TARIFFS[service_category]
        base_price = base_tariff['base']
        per_km = base_tariff['per_km']
        
        time_factor = EnvironmentalPricing.get_current_time_factor()
        weather_factor = EnvironmentalPricing.get_weather_factor(lat, lng)
        weather_data = EnvironmentalPricing.get_weather_data(lat, lng)
        
        # Calculs intermédiaires
        distance_cost = distance_km * per_km
        base_total = base_price + distance_cost
        time_surcharge = base_total * (time_factor - 1)
        weather_surcharge = base_total * (weather_factor - 1)
        final_price = base_total * time_factor * weather_factor
        final_price = ((final_price + 99) // 100) * 100
        
        # Labels
        time_label = EnvironmentalPricing._get_time_label()
        weather_label = weather_data.get('weather_desc', 'Conditions normales').capitalize()
        
        return {
            'base_price': int(base_price),
            'distance_cost': int(distance_cost),
            'base_total': int(base_total),
            'time_factor': time_factor,
            'time_label': time_label,
            'time_surcharge': int(time_surcharge),
            'weather_factor': weather_factor,
            'weather_label': weather_label,
            'weather_surcharge': int(weather_surcharge),
            'final_price': int(final_price),
            'service_category': service_category,
            'distance_km': distance_km
        }
    
    @staticmethod
    def _get_time_label():
        """Obtenir un label lisible pour l'heure"""
        now = datetime.datetime.now()
        hour = now.hour
        
        if 22 <= hour or hour < 6:
            return "🌙 Tarif de nuit (+30%)"
        elif 7 <= hour < 9:
            return "☀️ Heure de pointe matin (+40%)"
        elif 17 <= hour < 19:
            return "🌆 Heure de pointe soir (+40%)"
        elif now.weekday() >= 5:
            return "📅 Tarif week-end (+20%)"
        else:
            return "📍 Tarif normal"


# Singleton pour utilisation globale
environmental_pricing = EnvironmentalPricing()