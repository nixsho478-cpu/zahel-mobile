# nominatim_proxy.py - Proxy intelligent pour Nominatim (géocodage)
"""
Ce proxy sert d'intermédiaire entre votre carte Mapbox et l'API Nominatim d'OpenStreetMap.
Il permet de :
- Mettre en cache les résultats de recherche
- Respecter la limite de 1 requête/seconde imposée par Nominatim
- Formater les résultats exactement comme Mapbox les attend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import json
import os
from datetime import datetime
from functools import lru_cache

app = Flask(__name__)
CORS(app)  # Permet les requêtes depuis la carte HTML

# ===== CONFIGURATION =====
CACHE_FILE = "nominatim_cache.json"
REQUEST_DELAY = 1.1  # Secondes entre chaque requête (légèrement > 1s par sécurité)

# Variables globales
last_request_time = 0
cache = {}
request_count = 0

# ===== CHARGEMENT/SAUVEGARDE DU CACHE =====

def load_cache():
    """Charge le cache depuis le fichier JSON"""
    global cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            print(f"📦 Cache chargé: {len(cache)} entrées")
        except Exception as e:
            print(f"⚠️ Erreur chargement cache: {e}")
            cache = {}
    else:
        cache = {}
        print("📦 Nouveau cache créé")

def save_cache():
    """Sauvegarde le cache dans le fichier JSON (thread-safe)"""
    try:
        # ⭐ COPIER LE CACHE AVANT SAUVEGARDE (évite l'erreur "dictionary changed size")
        import copy
        cache_copy = copy.deepcopy(cache)
        
        # Ne garder que les 500 entrées les plus récentes
        if len(cache_copy) > 500:
            items = list(cache_copy.items())
            cache_copy = dict(items[-500:])
        
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_copy, f, ensure_ascii=False, indent=2)
        print(f"💾 Cache sauvegardé: {len(cache_copy)} entrées")
    except Exception as e:
        print(f"⚠️ Erreur sauvegarde cache: {e}")

# ===== FONCTION PRINCIPALE DE RECHERCHE =====

def search_nominatim(query, country='km', limit=8):
    """
    Recherche une adresse via Nominatim avec gestion du rate limiting
    """
    global last_request_time, request_count
    
    # 1. VÉRIFIER LE CACHE D'ABORD
    cache_key = f"{query.lower().strip()}_{country}"
    if cache_key in cache:
        print(f"📍 Cache HIT: '{query}'")
        return cache[cache_key]
    
    # 2. RESPECTER LA LIMITE DE 1 REQUÊTE PAR SECONDE
    now = time.time()
    time_since_last = now - last_request_time
    if time_since_last < REQUEST_DELAY:
        wait_time = REQUEST_DELAY - time_since_last
        print(f"⏳ Rate limiting: attente {wait_time:.2f}s")
        time.sleep(wait_time)
    
    # 3. CONSTRUIRE L'URL NOMINATIM
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': query,
        'countrycodes': country,
        'format': 'json',
        'limit': limit,
        'addressdetails': 1,
        'namedetails': 1
    }
    headers = {
        'User-Agent': 'ZAHEL-App/1.0 (contact: +2693608657)',
        'Accept-Language': 'fr,ar;q=0.9'  # Priorité français puis arabe
    }
    
    print(f"🌐 Nominatim: '{query}' (limite={country})")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        last_request_time = time.time()
        request_count += 1
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data)} résultats trouvés")
            
            # 4. FORMATER POUR MAPBOX (format exact attendu par le Geocoder)
            results = []
            for item in data:
                # Extraire le nom le plus pertinent
                name = item.get('name', '')
                if not name and 'namedetails' in item:
                    name = item['namedetails'].get('name', '')
                if not name:
                    name = item.get('display_name', '').split(',')[0]
                
                result = {
                    'id': f"osm-{item.get('place_id', '0')}",
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [float(item['lon']), float(item['lat'])]
                    },
                    'place_name': item.get('display_name', ''),
                    'text': name,
                    'center': [float(item['lon']), float(item['lat'])],
                    'place_type': ['poi'],
                    'properties': {
                        'title': name,
                        'address': item.get('address', {})
                    }
                }
                results.append(result)
            
            # 5. STOCKER DANS LE CACHE
            cache[cache_key] = results
            print(f"   💾 Stocké dans cache (total: {len(cache)} entrées)")
            
            # Sauvegarder périodiquement (toutes les 10 nouvelles entrées)
            if request_count % 10 == 0:
                save_cache()
            
            return results
        else:
            print(f"   ❌ Erreur Nominatim: {response.status_code}")
            return []
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout Nominatim")
        return []
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return []

# ===== ROUTES FLASK =====

@app.route('/search')
def search():
    """Endpoint de recherche - Appelé par la carte HTML"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    # Limiter aux Comores par défaut
    country = request.args.get('country', 'km')
    limit = int(request.args.get('limit', 8))
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔍 Recherche: '{query}'")
    results = search_nominatim(query, country, limit)
    
    return jsonify(results)

@app.route('/reverse')
def reverse_geocode():
    """Géocodage inverse: coordonnées → adresse"""
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    
    if not lat or not lng:
        return jsonify({'error': 'Coordonnées manquantes'}), 400
    
    cache_key = f"reverse_{lat}_{lng}"
    if cache_key in cache:
        print(f"📍 Cache HIT reverse: ({lat}, {lng})")
        return jsonify(cache[cache_key])
    
    # ⭐ RATE LIMITING (1 requête par seconde MAX)
    global last_request_time
    now = time.time()
    time_since_last = now - last_request_time
    if time_since_last < 1.0:
        wait_time = 1.0 - time_since_last
        print(f"⏳ Rate limiting reverse: attente {wait_time:.2f}s")
        time.sleep(wait_time)
    
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lng,
        'format': 'json',
        'addressdetails': 1,
        'zoom': 18
    }
    headers = {'User-Agent': 'ZAHEL-App/1.0'}
    
    try:
        print(f"🌐 Reverse Nominatim: ({lat}, {lng})")
        response = requests.get(url, params=params, headers=headers, timeout=8)  # 8 secondes
        last_request_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            result = {
                'display_name': data.get('display_name', ''),
                'address': data.get('address', {}),
                'name': data.get('name', '')
            }
            cache[cache_key] = result
            save_cache()  # Sauvegarde immédiate
            return jsonify(result)
        else:
            print(f"⚠️ Nominatim error: {response.status_code}")
            return jsonify({'error': f'Nominatim error {response.status_code}'}), 500
    except Exception as e:
        print(f"❌ Reverse geocode error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def stats():
    """Afficher les statistiques du proxy"""
    return jsonify({
        'cache_size': len(cache),
        'total_requests': request_count,
        'last_request': time.strftime('%H:%M:%S', time.localtime(last_request_time)) if last_request_time else None,
        'cache_keys_sample': list(cache.keys())[:10]
    })

@app.route('/clear-cache')
def clear_cache():
    """Vider le cache (utile pour les tests)"""
    global cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    return jsonify({'status': 'Cache vidé'})

# ===== DÉMARRAGE =====

# ===== DÉMARRAGE AVEC SERVEUR MULTI-THREAD =====

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔄 PROXY NOMINATIM POUR ZAHEL (MULTI-THREAD)")
    print("="*60)
    
    # Charger le cache existant
    load_cache()
    
    print(f"""
📋 CONFIGURATION:
   • Port: 5002
   • Cache: {len(cache)} entrées
   • Rate limit: {REQUEST_DELAY}s entre requêtes
   • Pays par défaut: Comores (km)
   • Mode: MULTI-THREAD (10 workers)

🛣️ ENDPOINTS:
   • GET /search?q=Pharmacie    → Recherche d'adresses
   • GET /reverse?lat=...&lng=... → Coordonnées → adresse
   • GET /stats                  → Statistiques du proxy
   • GET /clear-cache            → Vider le cache
""")
    
    print("="*60)
    print("⚡ Proxy démarré sur http://localhost:5002")
    print("="*60 + "\n")
    
    # ⭐⭐⭐ DÉMARRER AVEC UN SERVEUR MULTI-THREAD ⭐⭐⭐
    from waitress import serve
    
    try:
        serve(app, host='0.0.0.0', port=5002, threads=10)
    except ImportError:
        print("⚠️ Waitress non installé. Installation en cours...")
        import subprocess
        subprocess.run(['pip', 'install', 'waitress'], check=True)
        from waitress import serve
        serve(app, host='0.0.0.0', port=5002, threads=10)