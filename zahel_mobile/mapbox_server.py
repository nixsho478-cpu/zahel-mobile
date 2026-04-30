# mapbox_server.py - Version propre et fonctionnelle
import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from mapbox_state import MapboxState


class MapboxHandler(BaseHTTPRequestHandler):
    """Gère les requêtes HTTP de la carte"""
    
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            query_params = parse_qs(parsed.query)
        
            if path == '/' or path == '/index.html':
                depart_lat = query_params.get('depart_lat', [None])[0]
                depart_lng = query_params.get('depart_lng', [None])[0]
                arrivee_lat = query_params.get('arrivee_lat', [None])[0]
                arrivee_lng = query_params.get('arrivee_lng', [None])[0]
            
                if depart_lat and depart_lng and arrivee_lat and arrivee_lng:
                    html_path = os.path.join(os.path.dirname(__file__), 'carte_conducteur.html')
                    print(f"🗺️ Mode conducteur - chargement: {html_path}")
                else:
                    html_path = os.path.join(os.path.dirname(__file__), 'carte.html')
                    print(f"🗺️ Mode client - chargement: {html_path}")
            
                try:
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                
                    from config.mapbox_config import MapboxConfig
                    html_content = html_content.replace('MAPBOX_TOKEN_PLACEHOLDER', MapboxConfig.ACCESS_TOKEN)
                
                    if depart_lat and depart_lng and arrivee_lat and arrivee_lng:
                        html_content = html_content.replace('DEPART_LAT_PLACEHOLDER', depart_lat)
                        html_content = html_content.replace('DEPART_LNG_PLACEHOLDER', depart_lng)
                        html_content = html_content.replace('ARRIVEE_LAT_PLACEHOLDER', arrivee_lat)
                        html_content = html_content.replace('ARRIVEE_LNG_PLACEHOLDER', arrivee_lng)
                
                    content = html_content.encode('utf-8')
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Content-Length', len(content))
                    self.end_headers()
                    self.wfile.write(content)
                    print(f"✅ HTML chargé: {html_path}")
                
                except Exception as e:
                    print(f"❌ Erreur lecture HTML: {e}")
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<html><body>Erreur chargement carte</body></html>')
                
            elif path == '/suivi':
                html_content = self._generate_suivi_html(query_params)
                content = html_content.encode('utf-8')
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
                print(f"🗺️ Carte de suivi servie")
                
            elif path == '/status':
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                state = MapboxState.get_state()
                self.wfile.write(json.dumps(state).encode())
        
            elif path == '/click':
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "ok"}')
        
                params = parse_qs(parsed.query)
                if 'lat' in params and 'lng' in params:
                    try:
                        lat = float(params['lat'][0])
                        lng = float(params['lng'][0])
                        if hasattr(self.server, 'on_click') and self.server.on_click:
                            threading.Thread(
                                target=self.server.on_click,
                                args=(lat, lng),
                                daemon=True
                            ).start()
                    except (ValueError, IndexError):
                        pass
            else:
                self.send_response(404)
                self.end_headers()
        
        except (BrokenPipeError, ConnectionAbortedError):
            pass
        except Exception as e:
            print(f"Erreur handler GET: {e}")
            try:
                self.send_response(500)
                self.end_headers()
            except:
                pass
    
    def _generate_suivi_html(self, params):
        """Générer le HTML pour la carte de suivi - STYLE UBER"""
        course = params.get('course', [''])[0]
        depart_lat = params.get('depart_lat', ['-11.698'])[0]
        depart_lng = params.get('depart_lng', ['43.256'])[0]
        arrivee_lat = params.get('arrivee_lat', ['-11.71'])[0]
        arrivee_lng = params.get('arrivee_lng', ['43.265'])[0]
        
        from config.mapbox_config import MapboxConfig
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>ZAHEL - Suivi en temps réel</title>
    <script src="https://api.mapbox.com/mapbox-gl-js/v3.5.0/mapbox-gl.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/v3.5.0/mapbox-gl.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            height: 100vh; 
            display: flex; 
            flex-direction: column;
            background: #000;
        }}
        
        .header {{
            background: #000;
            color: white;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #333;
        }}
        .header h1 {{
            font-size: 20px;
            font-weight: 600;
        }}
        .header .status {{
            color: #00C853;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .header .status .dot {{
            width: 8px;
            height: 8px;
            background: #00C853;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
            100% {{ opacity: 1; }}
        }}
        
        #map {{ 
            flex: 1; 
            width: 100%; 
        }}
        
        .driver-panel {{
            background: white;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            border-bottom: 1px solid #eee;
        }}
        .driver-avatar {{
            width: 50px;
            height: 50px;
            background: #FF9800;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
        }}
        .driver-info {{
            flex: 1;
        }}
        .driver-name {{
            font-size: 16px;
            font-weight: 600;
            color: #000;
        }}
        .driver-vehicle {{
            font-size: 13px;
            color: #666;
            margin-top: 3px;
        }}
        .eta-badge {{
            background: #F5F5F5;
            padding: 8px 12px;
            border-radius: 20px;
            text-align: center;
        }}
        .eta-label {{
            font-size: 11px;
            color: #666;
        }}
        .eta-value {{
            font-size: 18px;
            font-weight: 700;
            color: #000;
        }}
        
        .actions {{
            background: white;
            padding: 12px 20px;
            display: flex;
            justify-content: space-around;
            border-top: 1px solid #eee;
        }}
        .action-btn {{
            background: none;
            border: none;
            color: #666;
            font-size: 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            padding: 8px 16px;
            border-radius: 8px;
            transition: background 0.2s;
        }}
        .action-btn:hover {{
            background: #F5F5F5;
        }}
        .action-btn .material-icons {{
            font-size: 24px;
        }}
        .action-btn.emergency {{
            color: #E53935;
        }}
        
        .center-btn {{
            position: absolute;
            bottom: 200px;
            right: 16px;
            background: white;
            border: none;
            border-radius: 50%;
            width: 44px;
            height: 44px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }}
        
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 12px 24px;
            border-radius: 30px;
            z-index: 2000;
        }}
        .loading.hidden {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚗 ZAHEL</h1>
        <div class="status">
            <span class="dot"></span>
            <span id="status-text">En approche</span>
        </div>
    </div>
    
    <div id="map"></div>
    
    <div class="loading" id="loading">
        <span>📍 Localisation du conducteur...</span>
    </div>
    
    <button class="center-btn" id="center-btn" title="Centrer sur le conducteur">
        <span class="material-icons">my_location</span>
    </button>
    
    <div class="driver-panel" id="driver-panel">
        <div class="driver-avatar" id="driver-initials">🚗</div>
        <div class="driver-info">
            <div class="driver-name" id="driver-name">Conducteur</div>
            <div class="driver-vehicle" id="driver-vehicle">Véhicule</div>
        </div>
        <div class="eta-badge">
            <div class="eta-label">Arrivée</div>
            <div class="eta-value" id="eta-display">-- min</div>
        </div>
    </div>
    
    <div class="actions">
        <button class="action-btn" onclick="window.location.href='tel:'">
            <span class="material-icons">phone</span>
            <span>Appeler</span>
        </button>
        <button class="action-btn" onclick="alert('Trajet partagé avec ZAHEL Sécurité')">
            <span class="material-icons">share</span>
            <span>Partager</span>
        </button>
        <button class="action-btn emergency" onclick="if(confirm('Contacter les urgences ?')) alert('Urgences: 122')">
            <span class="material-icons">warning</span>
            <span>Urgence</span>
        </button>
    </div>
    
    <script>
        mapboxgl.accessToken = '{MapboxConfig.ACCESS_TOKEN}';
        
        const map = new mapboxgl.Map({{
            container: 'map',
            style: 'mapbox://styles/mapbox/streets-v12',
            center: [{depart_lng}, {depart_lat}],
            zoom: 13
        }});
        
        map.addControl(new mapboxgl.NavigationControl(), 'top-left');
        
        let driverMarker = null;
        let departureMarker = null;
        let arrivalMarker = null;
        let currentRoute = null;
        const courseCode = '{course}';
        
        map.on('load', function() {{
            departureMarker = new mapboxgl.Marker({{color: '#4285F4'}})
                .setLngLat([{depart_lng}, {depart_lat}])
                .setPopup(new mapboxgl.Popup().setHTML('<b>📍 Point de départ</b>'))
                .addTo(map);
                
            arrivalMarker = new mapboxgl.Marker({{color: '#E53935'}})
                .setLngLat([{arrivee_lng}, {arrivee_lat}])
                .setPopup(new mapboxgl.Popup().setHTML('<b>🏁 Destination</b>'))
                .addTo(map);
                
            const bounds = new mapboxgl.LngLatBounds()
                .extend([{depart_lng}, {depart_lat}])
                .extend([{arrivee_lng}, {arrivee_lat}]);
            map.fitBounds(bounds, {{padding: 80}});
            
            updateDriverPosition();
        }});
        
        document.getElementById('center-btn').onclick = function() {{
            if (driverMarker) {{
                map.flyTo({{
                    center: driverMarker.getLngLat(),
                    zoom: 15
                }});
            }}
        }};
        
        function calculateETA(driverLat, driverLng, destLat, destLng) {{
            const R = 6371;
            const dLat = (destLat - driverLat) * Math.PI / 180;
            const dLon = (destLng - driverLng) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                      Math.cos(driverLat * Math.PI / 180) * Math.cos(destLat * Math.PI / 180) *
                      Math.sin(dLon/2) * Math.sin(dLon/2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            const distance = R * c;
            const minutes = Math.round(distance * 4);
            return minutes > 0 ? minutes : 1;
        }}
        
        function updateRoute(startLat, startLng, endLat, endLng) {{
            const url = `https://api.mapbox.com/directions/v5/mapbox/driving/${{startLng}},${{startLat}};${{endLng}},${{endLat}}?geometries=geojson&access_token=${{mapboxgl.accessToken}}`;
            
            fetch(url)
                .then(r => r.json())
                .then(data => {{
                    if (data.routes && data.routes[0]) {{
                        const route = data.routes[0];
                        const coordinates = route.geometry.coordinates;
                        
                        if (currentRoute) {{
                            if (map.getLayer('route')) map.removeLayer('route');
                            if (map.getSource('route')) map.removeSource('route');
                        }}
                        
                        map.addSource('route', {{
                            type: 'geojson',
                            data: {{
                                type: 'Feature',
                                geometry: {{
                                    type: 'LineString',
                                    coordinates: coordinates
                                }}
                            }}
                        }});
                        
                        map.addLayer({{
                            id: 'route',
                            type: 'line',
                            source: 'route',
                            paint: {{
                                'line-color': '#4285F4',
                                'line-width': 4,
                                'line-opacity': 0.8
                            }}
                        }});
                        
                        currentRoute = coordinates;
                    }}
                }})
                .catch(e => console.error('Erreur itinéraire:', e));
        }}
        
        function updateDriverPosition() {{
            document.getElementById('loading').classList.remove('hidden');
            
            fetch('https://zahel-comores.com/api/courses/' + courseCode + '/statut')
                .then(r => r.json())
                .then(data => {{
                    document.getElementById('loading').classList.add('hidden');
                    
                    if (data.success && data.course) {{
                        const course = data.course;
                        const driver = course.conducteur;
                        
                        if (driver) {{
                            document.getElementById('driver-name').textContent = driver.nom || 'Conducteur';
                            document.getElementById('driver-vehicle').textContent = 
                                (driver.marque_vehicule || '') + ' ' + (driver.modele_vehicule || 'Véhicule');
                            document.getElementById('driver-initials').textContent = '🚗';
                            
                            if (driver.telephone) {{
                                document.querySelector('.action-btn').onclick = 
                                    () => window.location.href = 'tel:' + driver.telephone;
                            }}
                            
                            const statusMap = {{
                                'en_recherche': 'Recherche conducteur...',
                                'acceptee': 'En approche',
                                'en_cours': 'En course',
                                'terminee': 'Terminée'
                            }};
                            document.getElementById('status-text').textContent = 
                                statusMap[course.statut] || course.statut;
                            
                            if (driver.latitude && driver.longitude) {{
                                const lng = driver.longitude;
                                const lat = driver.latitude;
                                
                                if (driverMarker) {{
                                    driverMarker.setLngLat([lng, lat]);
                                }} else {{
                                    const el = document.createElement('div');
                                    el.style.background = '#FF9800';
                                    el.style.width = '40px';
                                    el.style.height = '40px';
                                    el.style.borderRadius = '50%';
                                    el.style.border = '3px solid white';
                                    el.style.boxShadow = '0 2px 10px rgba(0,0,0,0.3)';
                                    el.style.display = 'flex';
                                    el.style.alignItems = 'center';
                                    el.style.justifyContent = 'center';
                                    el.style.fontSize = '20px';
                                    el.innerHTML = '🚗';
                                    
                                    driverMarker = new mapboxgl.Marker(el)
                                        .setLngLat([lng, lat])
                                        .setPopup(new mapboxgl.Popup().setHTML('<b>🚗 ' + (driver.nom || 'Conducteur') + '</b>'))
                                        .addTo(map);
                                }}
                                
                                const eta = calculateETA(lat, lng, {arrivee_lat}, {arrivee_lng});
                                document.getElementById('eta-display').textContent = eta + ' min';
                                
                                // Déterminer la destination selon le statut
                                let destLat, destLng;
                                if (course.statut === 'acceptee') {{
                                    destLat = {depart_lat};
                                    destLng = {depart_lng};
                                }} else {{
                                    destLat = {arrivee_lat};
                                    destLng = {arrivee_lng};
                                }}
                                updateRoute(lat, lng, destLat, destLng);
                            }}
                        }}
                    }}
                }})
                .catch(e => {{
                    console.error('Erreur:', e);
                    document.getElementById('loading').classList.add('hidden');
                }});
        }}
        
        setInterval(updateDriverPosition, 3000);
    </script>
</body>
</html>'''
    
    def do_POST(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            if path == '/set_coords':
                data = json.loads(post_data.decode('utf-8'))
                
                if 'depart' in data:
                    MapboxState.add_marker(
                        data['depart']['lat'],
                        data['depart']['lng'],
                        'depart'
                    )
                    MapboxState.set_depart(data['depart']['lat'], data['depart']['lng'])
                
                if 'arrivee' in data:
                    MapboxState.add_marker(
                        data['arrivee']['lat'],
                        data['arrivee']['lng'],
                        'arrivee'
                    )
                    MapboxState.set_arrivee(data['arrivee']['lat'], data['arrivee']['lng'])
                
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
                
            elif path == '/confirm':
                data = json.loads(post_data.decode('utf-8'))
                
                if 'depart' in data and 'arrivee' in data:
                    MapboxState.set_depart(data['depart']['lat'], data['depart']['lng'])
                    MapboxState.set_arrivee(data['arrivee']['lat'], data['arrivee']['lng'])
                    MapboxState.set_confirmed(True)
                    
                    if hasattr(self.server, 'on_confirm') and self.server.on_confirm:
                        threading.Thread(
                            target=self.server.on_confirm,
                            args=(data['depart'], data['arrivee']),
                            daemon=True
                        ).start()
                
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'confirmed'}).encode())
                
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            print(f"Erreur handler POST: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass


class MapboxServer:
    """Serveur local pour la carte Mapbox"""
    
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.on_click_callback = None
        self.on_confirm = None
        self.html_content = None
        self._is_running = False
    
    def set_html(self, html_content):
        self.html_content = html_content
    
    def set_on_click(self, callback):
        self.on_click_callback = callback
    
    def add_marker(self, lat, lng, marker_type):
        MapboxState.add_marker(lat, lng, marker_type)
    
    def set_route(self, coordinates):
        MapboxState.set_route(coordinates)
    
    def clear(self):
        MapboxState.clear()
    
    def start(self):
        if self._is_running:
            return f"http://localhost:{self.port}"
            
        try:
            self.server = HTTPServer(('localhost', self.port), MapboxHandler)
            self.server.html_content = self.html_content
            self.server.on_click = self.on_click_callback
            self.server.on_confirm = self.on_confirm
            
            thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            thread.start()
            
            import time
            time.sleep(0.5)
            
            self._is_running = True
            print(f"✅ Serveur Mapbox démarré sur http://localhost:{self.port}")
            return f"http://localhost:{self.port}"
            
        except Exception as e:
            print(f"❌ Erreur démarrage serveur: {e}")
            return None
    
    def stop(self):
        if self.server:
            self._is_running = False
            self.server.shutdown()
            self.server = None