# preload_comores_tiles.py - Précharger les tuiles des Comores
import os
import requests
import threading
import time
from kivy.clock import Clock

class ComoresTilePreloader:
    """Précharge les tuiles OSM des zones principales des Comores"""
    
    def __init__(self, cache_dir="cache/osm_tiles_comores"):
        self.cache_dir = os.path.join(os.getcwd(), cache_dir)
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # Zones principales des Comores à précharger
        self.comores_zones = [
            {
                'name': 'Moroni Centre',
                'center': (-11.698, 43.256),
                'zoom_range': (13, 16),  # Zoom 13 à 16
                'radius_km': 2  # Rayon de 2km
            },
            {
                'name': 'Iconi',
                'center': (-11.704, 43.261),
                'zoom_range': (13, 15),
                'radius_km': 1.5
            },
            {
                'name': 'Port de Moroni',
                'center': (-11.692, 43.252),
                'zoom_range': (14, 16),
                'radius_km': 1
            },
            {
                'name': 'Aéroport',
                'center': (-11.533, 43.267),
                'zoom_range': (13, 14),
                'radius_km': 2
            }
        ]
        
        # Serveurs OSM alternatifs
        self.tile_servers = [
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "https://tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png"
        ]
    
    def latlon_to_tile(self, lat, lon, zoom):
        """Convertir lat/lon en coordonnées tuile OSM"""
        import math
        
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        
        return x, y
    
    def download_tile(self, z, x, y):
        """Télécharger une tuile"""
        import hashlib
        
        for server in self.tile_servers:
            try:
                url = server.format(z=z, x=x, y=y)
                tile_key = hashlib.md5(url.encode()).hexdigest()
                tile_path = os.path.join(self.cache_dir, f"{tile_key}.png")
                
                # Si déjà en cache
                if os.path.exists(tile_path):
                    continue
                
                # Télécharger
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(tile_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"  💾 {z}/{x}/{y} -> {tile_key}.png")
                    return True
                    
            except Exception as e:
                continue
        
        return False
    
    def preload_zone(self, zone):
        """Précharger une zone"""
        print(f"📍 Préchargement: {zone['name']}")
        
        center_lat, center_lon = zone['center']
        min_zoom, max_zoom = zone['zoom_range']
        
        # Pour chaque niveau de zoom
        for z in range(min_zoom, max_zoom + 1):
            # Tuile centrale
            center_x, center_y = self.latlon_to_tile(center_lat, center_lon, z)
            
            # Précharger un carré autour
            radius_tiles = 2  # 2 tuiles dans chaque direction
            
            for dx in range(-radius_tiles, radius_tiles + 1):
                for dy in range(-radius_tiles, radius_tiles + 1):
                    x = center_x + dx
                    y = center_y + dy
                    
                    self.download_tile(z, x, y)
                    time.sleep(0.1)  # Pour ne pas surcharger les serveurs
        
        print(f"  ✅ {zone['name']} préchargé")
    
    def start_preloading(self, background=True):
        """Démarrer le préchargement"""
        print("🌍 DÉMARRAGE PRÉCHARGEMENT COMORES")
        print("=" * 50)
        
        if background:
            # En arrière-plan
            thread = threading.Thread(target=self._preload_all, daemon=True)
            thread.start()
            print("✅ Préchargement démarré en arrière-plan")
        else:
            # En foreground
            self._preload_all()
    
    def _preload_all(self):
        """Précharger toutes les zones"""
        for zone in self.comores_zones:
            self.preload_zone(zone)
        
        print("=" * 50)
        print("🎉 PRÉCHARGEMENT TERMINÉ")
        
        # Afficher statistiques
        tile_count = len([f for f in os.listdir(self.cache_dir) if f.endswith('.png')])
        print(f"📦 Tuiles en cache: {tile_count}")
        
        total_size = sum(os.path.getsize(os.path.join(self.cache_dir, f)) 
                        for f in os.listdir(self.cache_dir) if f.endswith('.png'))
        print(f"💾 Taille cache: {total_size/1024/1024:.2f} MB")

# Instance globale
comores_preloader = ComoresTilePreloader()

if __name__ == "__main__":
    # Tester le préchargement
    comores_preloader.start_preloading(background=False)