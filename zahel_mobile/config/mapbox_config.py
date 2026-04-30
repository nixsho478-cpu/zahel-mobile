# mapbox_config.py - Configuration Mapbox pour ZAHEL

class MapboxConfig:
    """Configuration spécifique à Mapbox"""
    
    # ===== VOTRE TOKEN MAPBOX =====
    ACCESS_TOKEN = "pk.eyJ1IjoiZWwtaGFkNiIsImEiOiJjbW42ZnFiMWIwNDk0MnhzYmM3YmtwdWdiIn0.Q49AgJpKyLD4ifCWmlH74w"
    
    # ===== STYLES DISPONIBLES =====
    STYLES = {
        'streets': 'mapbox/streets-v12',
        'outdoors': 'mapbox/outdoors-v12',
        'light': 'mapbox/light-v11',
        'dark': 'mapbox/dark-v11',
        'satellite': 'mapbox/satellite-v9',
        'satellite_streets': 'mapbox/satellite-streets-v12',
        'navigation_day': 'mapbox/navigation-day-v1',
        'navigation_night': 'mapbox/navigation-night-v1'
    }
    
    # ===== PARAMÈTRES PAR DÉFAUT =====
    DEFAULT_STYLE = 'streets'
    DEFAULT_ZOOM = 14
    MIN_ZOOM = 10
    MAX_ZOOM = 19
    
    # Centre par défaut (Moroni, Comores)
    DEFAULT_LAT = -11.6980
    DEFAULT_LNG = 43.2560
    
    # Rayon de recherche (km)
    DEFAULT_SEARCH_RADIUS = 5
    
    @classmethod
    def get_style_url(cls, style_name=None):
        """Retourne l'URL du style Mapbox"""
        style = style_name or cls.DEFAULT_STYLE
        style_id = cls.STYLES.get(style, cls.STYLES['streets'])
        return f"https://api.mapbox.com/styles/v1/{style_id}/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={cls.ACCESS_TOKEN}"
    
    @classmethod
    def get_geocoding_url(cls, address):
        """Retourne l'URL pour le géocodage"""
        from urllib.parse import quote
        encoded_address = quote(address)
        return f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded_address}.json?access_token={cls.ACCESS_TOKEN}&limit=5&country=km"
    
    @classmethod
    def get_directions_url(cls, start_lat, start_lng, end_lat, end_lng):
        """Retourne l'URL pour les directions"""
        return f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_lng},{start_lat};{end_lng},{end_lat}?access_token={cls.ACCESS_TOKEN}&geometries=geojson&overview=full&steps=true"
    
    @classmethod
    def get_static_map_url(cls, lat, lng, zoom=14, width=400, height=400):
        """Retourne l'URL pour une carte statique"""
        style_id = cls.STYLES.get(cls.DEFAULT_STYLE, cls.STYLES['streets'])
        return f"https://api.mapbox.com/styles/v1/{style_id}/static/{lng},{lat},{zoom}/{width}x{height}?access_token={cls.ACCESS_TOKEN}"