# config.py - Configuration de l'application ZAHEL

import os

class Config:
    """Configuration centrale de l'application"""
    
    # URL de l'API (à modifier pour la production)
    API_BASE_URL = os.environ.get('ZAHEL_API_URL', 'https://zahel-comores.com')
    
    # Paramètres de l'application
    APP_NAME = "ZAHEL"
    APP_VERSION = "1.0.0"
    
    # Paramètres de session
    SESSION_DURATION = 31536000  # 1 an en secondes
    SESSION_FILE = 'session.json'
    
    # Paramètres de carte
    MAP_CACHE_DIR = os.path.join(os.getcwd(), "cache", "osm_tiles_comores")
    MAP_DEFAULT_ZOOM = 14
    MAP_DEFAULT_CENTER = (-11.6980, 43.2560)  # Moroni
    
    # Paramètres de notification
    NOTIFICATION_CHECK_INTERVAL = 30  # secondes
    NOTIFICATION_SOUND_ENABLED = True
    
    # Paramètres WhatsApp
    WHATSAPP_AGENCE_NUMBER = "2693608657"
    
    @classmethod
    def get_api_url(cls):
        """Retourne l'URL de l'API avec gestion d'environnement"""
        return cls.API_BASE_URL

    # ⭐ NOUVEAU : Contrôle des logs
    DEBUG_LOGS = {
        'course_code': False,      # Logs "Pas encore de course_code"
        'api_calls': True,          # Logs des appels API
        'notifications': True,      # Logs des notifications
        'position_updates': False,  # Logs des mises à jour de position
    }
    
    @classmethod
    def should_log(cls, category):
        """Vérifier si une catégorie de log doit être affichée"""
        return cls.DEBUG_LOGS.get(category, False)

    # ========== MAPBOX CONFIGURATION ==========
    MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiZWwtaGFkNiIsImEiOiJjbW42ZnFiMWIwNDk0MnhzYmM3YmtwdWdiIn0.Q49AgJpKyLD4ifCWmlH74w"
    MAPBOX_STYLE = "mapbox/streets-v12"
    MAPBOX_NAVIGATION_STYLE = "mapbox/navigation-day-v1"
    
    # Paramètres de la carte
    MAPBOX_DEFAULT_ZOOM = 14
    MAPBOX_DEFAULT_LAT = -11.6980  # Moroni
    MAPBOX_DEFAULT_LNG = 43.2560
    
    # Mode économie de données
    MAPBOX_CACHE_ENABLED = True
    MAPBOX_CACHE_SIZE_MB = 100

    # Clé API OpenWeatherMap (gratuite - 1 000 000 appels/mois)
    OPENWEATHER_API_KEY = "23bb60ea78dcfb3f5736236b3acbc8f4"