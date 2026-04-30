# mapbox_mapview.py - Carte Mapbox pour Kivy
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.graphics import Color, Rectangle
import os
import math
from urllib.parse import quote

# Import de la configuration
from config.mapbox_config import MapboxConfig


class MapboxMapView(Widget):
    """
    Widget de carte utilisant Mapbox
    Affiche des tuiles Mapbox avec cache local
    """
    
    def __init__(self, **kwargs):
        # Récupérer les paramètres
        self.lat = kwargs.pop('lat', MapboxConfig.DEFAULT_LAT)
        self.lng = kwargs.pop('lng', MapboxConfig.DEFAULT_LNG)
        self.zoom = kwargs.pop('zoom', MapboxConfig.DEFAULT_ZOOM)
        self.style = kwargs.pop('style', MapboxConfig.DEFAULT_STYLE)
        
        super(MapboxMapView, self).__init__(**kwargs)
        
        # Taille des tuiles en pixels
        self.tile_size = 256
        
        # Cache des tuiles
        self.cache_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'cache', 
            'mapbox_tiles'
        )
        self._ensure_cache_dir()
        
        # Dictionnaire des tuiles chargées
        self.tiles = {}
        
        # Conteneur pour les tuiles
        self.tile_container = Widget(size_hint=(1, 1))
        self.add_widget(self.tile_container)
        
        # État
        self._loading_tiles = False
        self._last_zoom = self.zoom
        
        # Charger les tuiles
        Clock.schedule_once(self._load_visible_tiles, 0.5)
        
        print(f"🗺️ MapboxMapView créée: centre=({self.lat}, {self.lng}), zoom={self.zoom}")
    
    def _ensure_cache_dir(self):
        """Crée le dossier de cache s'il n'existe pas"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            print(f"📁 Dossier cache créé: {self.cache_dir}")
    
    def _lat_lng_to_tile(self, lat, lng, zoom):
        """Convertit des coordonnées en indices de tuile"""
        n = 2.0 ** zoom
        x = (lng + 180.0) / 360.0 * n
        lat_rad = math.radians(lat)
        y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
        return int(x), int(y)
    
    def _tile_to_lat_lng(self, x, y, zoom):
        """Convertit un indice de tuile en coordonnées approximatives"""
        n = 2.0 ** zoom
        lng = x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat = math.degrees(lat_rad)
        return lat, lng
    
    def _get_tile_url(self, x, y, zoom):
        """Retourne l'URL d'une tuile Mapbox"""
        style_id = MapboxConfig.STYLES.get(self.style, MapboxConfig.STYLES['streets'])
        return f"https://api.mapbox.com/styles/v1/{style_id}/tiles/{zoom}/{x}/{y}@2x?access_token={MapboxConfig.ACCESS_TOKEN}"
    
    def _get_cache_path(self, x, y, zoom):
        """Retourne le chemin de cache pour une tuile"""
        return os.path.join(self.cache_dir, f"{zoom}_{x}_{y}.png")
    
    def _load_tile(self, x, y, zoom):
        """Charge une tuile depuis cache ou réseau"""
        tile_key = f"{zoom}_{x}_{y}"
        
        # Déjà chargée ?
        if tile_key in self.tiles:
            return
        
        cache_path = self._get_cache_path(x, y, zoom)
        
        # Vérifier le cache
        if os.path.exists(cache_path):
            self._add_tile_from_file(cache_path, x, y, zoom)
            return
        
        # Charger depuis réseau
        url = self._get_tile_url(x, y, zoom)
        
        def on_success(req, result):
            try:
                # Sauvegarder en cache
                with open(cache_path, 'wb') as f:
                    f.write(result)
                self._add_tile_from_file(cache_path, x, y, zoom)
            except Exception as e:
                print(f"⚠️ Erreur sauvegarde tuile {tile_key}: {e}")
        
        def on_failure(req, error):
            print(f"⚠️ Erreur chargement tuile {tile_key}: {error}")
        
        # Lancer la requête
        UrlRequest(url, on_success=on_success, on_failure=on_failure)
    
    def _add_tile_from_file(self, filepath, x, y, zoom):
        """Ajoute une tuile à partir d'un fichier"""
        tile_key = f"{zoom}_{x}_{y}"
        
        if tile_key in self.tiles:
            return
        
        try:
            img = Image(
                source=filepath,
                size=(self.tile_size, self.tile_size),
                size_hint=(None, None),
                allow_stretch=False,
                keep_ratio=False
            )
            self.tile_container.add_widget(img)
            self.tiles[tile_key] = img
            
            # Mettre à jour la position
            self._update_tile_position(x, y, zoom, img)
            
        except Exception as e:
            print(f"⚠️ Erreur ajout tuile {tile_key}: {e}")
    
    def _update_tile_position(self, x, y, zoom, widget):
        """Calcule et met à jour la position d'une tuile"""
        # Coordonnées du centre en pixels
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Position du centre en tuiles
        tile_center_x, tile_center_y = self._lat_lng_to_tile(self.lat, self.lng, zoom)
        
        # Décalage du centre en pixels
        n = 2.0 ** zoom
        lng_center = self.lng
        lat_center = self.lat
        
        # Calcul du décalage
        offset_x = center_x - (tile_center_x * self.tile_size)
        offset_y = center_y - (tile_center_y * self.tile_size)
        
        # Position de la tuile
        widget.pos = (x * self.tile_size + offset_x, y * self.tile_size + offset_y)
    
    def _update_all_tile_positions(self):
        """Met à jour la position de toutes les tuiles"""
        for tile_key, widget in self.tiles.items():
            parts = tile_key.split('_')
            if len(parts) == 3:
                zoom = int(parts[0])
                x = int(parts[1])
                y = int(parts[2])
                if zoom == self.zoom:
                    self._update_tile_position(x, y, zoom, widget)
    
    def _load_visible_tiles(self, dt=None):
        """Charge les tuiles visibles"""
        if not self.parent or self.width == 0 or self.height == 0:
            Clock.schedule_once(self._load_visible_tiles, 0.2)
            return
        
        # Supprimer les tuiles d'un autre zoom
        if self._last_zoom != self.zoom:
            to_remove = []
            for tile_key in self.tiles:
                zoom = int(tile_key.split('_')[0])
                if zoom != self.zoom:
                    to_remove.append(tile_key)
            for tile_key in to_remove:
                self.tile_container.remove_widget(self.tiles[tile_key])
                del self.tiles[tile_key]
            self._last_zoom = self.zoom
        
        # Calculer les tuiles visibles
        tile_x, tile_y = self._lat_lng_to_tile(self.lat, self.lng, self.zoom)
        
        # Nombre de tuiles nécessaires pour couvrir l'écran
        tiles_wide = int(self.width / self.tile_size) + 2
        tiles_high = int(self.height / self.tile_size) + 2
        
        # Charger les tuiles
        for dx in range(-tiles_wide, tiles_wide + 1):
            for dy in range(-tiles_high, tiles_high + 1):
                x = tile_x + dx
                y = tile_y + dy
                self._load_tile(x, y, self.zoom)
        
        # Mettre à jour les positions
        self._update_all_tile_positions()
    
    def center_on(self, lat, lng):
        """Centre la carte sur des coordonnées"""
        self.lat = lat
        self.lng = lng
        Clock.schedule_once(self._load_visible_tiles, 0.1)
    
    def set_zoom(self, zoom):
        """Définit le niveau de zoom"""
        new_zoom = max(MapboxConfig.MIN_ZOOM, min(MapboxConfig.MAX_ZOOM, zoom))
        if new_zoom != self.zoom:
            self.zoom = new_zoom
            Clock.schedule_once(self._load_visible_tiles, 0.1)
    
    def zoom_in(self):
        """Zoom avant"""
        self.set_zoom(self.zoom + 1)
    
    def zoom_out(self):
        """Zoom arrière"""
        self.set_zoom(self.zoom - 1)
    
    def on_size(self, *args):
        """Quand la taille change, recharger les tuiles"""
        Clock.schedule_once(self._load_visible_tiles, 0.1)
    
    def on_pos(self, *args):
        """Quand la position change, mettre à jour les positions"""
        self._update_all_tile_positions()