# osm_proxy.py - Proxy local pour contourner les limites OSM
import os
import requests
import sqlite3
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class OSMTileCache:
    """Cache local des tuiles OSM"""
    
    def __init__(self, cache_dir="cache/osm_tiles"):
        self.cache_dir = os.path.join(os.getcwd(), cache_dir)
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # Base de données pour metadata
        self.db_path = os.path.join(self.cache_dir, "osm_cache.db")
        self.init_db()
    
    def init_db(self):
        """Initialiser la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tiles (
                tile_key TEXT PRIMARY KEY,
                url TEXT,
                filename TEXT,
                size INTEGER,
                accessed INTEGER DEFAULT 0,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_tile(self, z, x, y):
        """Récupérer une tuile (zoom, x, y)"""
        tile_key = f"{z}_{x}_{y}"
        cache_file = os.path.join(self.cache_dir, f"{tile_key}.png")
        
        # Vérifier le cache
        if os.path.exists(cache_file):
            # Mettre à jour le compteur d'accès
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tiles SET accessed = accessed + 1 WHERE tile_key = ?",
                (tile_key,)
            )
            conn.commit()
            conn.close()
            
            print(f"📦 Cache hit: {tile_key}")
            with open(cache_file, 'rb') as f:
                return f.read()
        
        # Télécharger depuis OSM avec retry
        urls = [
            f"https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            f"https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
            f"https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
            f"https://c.tile.openstreetmap.org/{z}/{x}/{y}.png"
        ]
        
        for url in urls:
            try:
                print(f"🌐 Download: {url}")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    # Sauvegarder dans le cache
                    with open(cache_file, 'wb') as f:
                        f.write(response.content)
                    
                    # Enregistrer dans la DB
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        '''INSERT OR REPLACE INTO tiles 
                           (tile_key, url, filename, size, accessed) 
                           VALUES (?, ?, ?, ?, 1)''',
                        (tile_key, url, cache_file, len(response.content))
                    )
                    conn.commit()
                    conn.close()
                    
                    print(f"💾 Saved: {tile_key} ({len(response.content)} bytes)")
                    return response.content
                
            except Exception as e:
                print(f"❌ Failed {url}: {e}")
                continue
        
        # Si toutes les URLs échouent, retourner une tuile vide
        print(f"⚠️  All OSM servers failed for {tile_key}")
        return self.create_empty_tile()
    
    def create_empty_tile(self):
        """Créer une tuile vide (carré gris)"""
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (256, 256), color=(220, 220, 220))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "OSM Tile\nUnavailable", fill=(100, 100, 100))
        
        import io
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

# Instance globale
osm_cache = OSMTileCache()

# Serveur proxy HTTP simple
class TileProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Servir les tuiles OSM via proxy local"""
        try:
            # Extraire z/x/y du chemin
            # Format: /tiles/{z}/{x}/{y}.png
            parts = self.path.strip('/').split('/')
            
            if len(parts) == 4 and parts[0] == 'tiles':
                z, x, y = parts[1], parts[2], parts[3].replace('.png', '')
                
                # Récupérer la tuile
                tile_data = osm_cache.get_tile(z, x, y)
                
                # Envoyer la réponse
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.end_headers()
                self.wfile.write(tile_data)
                
                print(f"✅ Served: {z}/{x}/{y}")
            else:
                self.send_error(404)
                
        except Exception as e:
            print(f"❌ Proxy error: {e}")
            self.send_error(500)
    
    def log_message(self, format, *args):
        """Désactiver les logs du serveur"""
        pass

def start_proxy_server(port=8765):
    """Démarrer le serveur proxy en arrière-plan"""
    server = HTTPServer(('localhost', port), TileProxyHandler)
    print(f"🚀 OSM Proxy started on http://localhost:{port}")
    server.serve_forever()

# Démarrer le proxy dans un thread
proxy_thread = threading.Thread(target=start_proxy_server, daemon=True)
proxy_thread.start()