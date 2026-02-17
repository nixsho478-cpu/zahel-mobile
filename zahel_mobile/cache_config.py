# cache_config.py - Configuration du cache OSM
import os
import sqlite3
import hashlib
from kivy.core.image import Image

class OSMCacheManager:
    """Gestionnaire de cache pour les tuiles OSM"""
    
    def __init__(self, cache_dir="cache/osm_tiles"):
        self.cache_dir = os.path.join(os.getcwd(), cache_dir)
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            print(f"📁 Cache OSM: {self.cache_dir}")
        
        # Base de données pour suivre les tuiles
        self.db_path = os.path.join(self.cache_dir, "tiles.db")
        self.init_database()
        
    def init_database(self):
        """Initialiser la base de données SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tiles (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                filename TEXT,
                size INTEGER,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_cached_tile(self, url):
        """Récupérer une tuile depuis le cache"""
        import requests
        
        # Générer un nom de fichier unique
        tile_hash = hashlib.md5(url.encode()).hexdigest()
        filename = f"{tile_hash}.png"
        filepath = os.path.join(self.cache_dir, filename)
        
        # Vérifier si le fichier existe
        if os.path.exists(filepath):
            print(f"📦 CACHE: {os.path.basename(filename)}")
            return filepath
        
        # Sinon, télécharger
        print(f"🌐 DOWNLOAD: {os.path.basename(url)}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Sauvegarder
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Enregistrer dans la DB
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO tiles (url, filename, size) VALUES (?, ?, ?)",
                    (url, filename, len(response.content))
                )
                conn.commit()
                conn.close()
                
                print(f"💾 SAVED: {filename} ({len(response.content)} bytes)")
                return filepath
        except Exception as e:
            print(f"❌ Download error: {e}")
        
        return url  # Retourner l'URL originale si échec

# Instance globale
osm_cache = OSMCacheManager()