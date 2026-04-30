# mapbox_webview.py - Version avec stockage des marqueurs dans le serveur
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import os
import json
import webbrowser

from config.mapbox_config import MapboxConfig
from mapbox_server import MapboxServer


class MapboxWebView(Widget):
    def __init__(self, **kwargs):
        self.lat = kwargs.pop('lat', MapboxConfig.DEFAULT_LAT)
        self.lng = kwargs.pop('lng', MapboxConfig.DEFAULT_LNG)
        self.zoom = kwargs.pop('zoom', MapboxConfig.DEFAULT_ZOOM)
        
        super(MapboxWebView, self).__init__(**kwargs)
        
        self.server = None
        self.on_click_callback = None
        self.map_url = None
        
        self.layout = BoxLayout(orientation='vertical', size_hint=(1, 1))
        self.add_widget(self.layout)
        
        Clock.schedule_once(self._init_map, 0.1)
        print(f"🗺️ MapboxWebView initialisée")
    
    def _init_map(self, dt):
        try:
            self.server = MapboxServer()
            self.server.set_on_click(self._on_map_click)
            
            html_content = self._generate_html()
            self.server.set_html(html_content)
            
            url = self.server.start()
            
            if url:
                self.map_url = url
                self._create_browser_button()
            else:
                self._create_error_label()
                
        except Exception as e:
            print(f"❌ Erreur initialisation: {e}")
            self._create_error_label()
    
    def _generate_html(self):
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>ZAHEL Map</title>
    <script src="https://api.mapbox.com/mapbox-gl-js/v3.5.0/mapbox-gl.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/v3.5.0/mapbox-gl.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; }}
        body {{ margin: 0; padding: 0; overflow: hidden; height: 100vh; }}
        #map {{ position: absolute; top: 0; bottom: 0; width: 100%; height: 100%; }}
        .marker-depart {{
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%234285F4" width="36px" height="36px"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/></svg>');
            background-size: cover; width: 36px; height: 36px; cursor: pointer;
        }}
        .marker-arrivee {{
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23E53935" width="36px" height="36px"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/></svg>');
            background-size: cover; width: 36px; height: 36px; cursor: pointer;
        }}
        .marker-voiture {{
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23FF9800" width="36px" height="36px"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg>');
            background-size: cover; width: 36px; height: 36px; cursor: pointer;
        }}
        .controls {{
            position: absolute; bottom: 20px; right: 10px; background: white;
            border-radius: 8px; padding: 5px; z-index: 1000;
        }}
        .controls button {{
            background: #4285F4; color: white; border: none; width: 40px; height: 40px;
            margin: 2px; border-radius: 4px; font-size: 20px; cursor: pointer;
        }}
        .status {{
            position: absolute; top: 10px; left: 10px; right: 10px;
            background: rgba(0,0,0,0.7); color: white; padding: 8px;
            border-radius: 8px; font-size: 12px; text-align: center;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="controls">
        <button id="zoom-in">+</button>
        <button id="zoom-out">-</button>
        <button id="locate">📍</button>
        <button id="refresh">🔄</button>
    </div>
    <div id="status" class="status">ZAHEL - Cliquez sur la carte</div>
    
    <script>
        mapboxgl.accessToken = '{MapboxConfig.ACCESS_TOKEN}';
        
        const map = new mapboxgl.Map({{
            container: 'map',
            style: 'mapbox://styles/mapbox/streets-v12',
            center: [{self.lng}, {self.lat}],
            zoom: {self.zoom}
        }});
        
        map.addControl(new mapboxgl.NavigationControl(), 'top-right');
        
        let markers = [];
        let currentRoute = null;
        
        function loadData() {{
            fetch('/status')
                .then(r => r.json())
                .then(data => {{
                    console.log('Données reçues:', data);

                    markers.forEach(m => m.remove());
                    markers = [];
                    
                    if (data.markers) {{
                        data.markers.forEach(m => {{
                            const el = document.createElement('div');
                            if (m.type === 'arrivee') {{
                                el.className = 'marker-arrivee';
                            }} else if (m.type === 'voiture') {{
                                el.className = 'marker-voiture';
                            }} else {{
                                el.className = 'marker-depart';
                            }}
                            const marker = new mapboxgl.Marker(el).setLngLat([m.lng, m.lat]).addTo(map);
                            markers.push(marker);
                        }});
                        if (data.markers.length > 0) {{
                            document.getElementById('status').innerHTML = `📍 ${{data.markers.length}} marqueur(s) sur la carte`;
                        }}
                    }}

                    console.log('Route reçue:', data.route);
                    
                    if (data.route && data.route.length > 0) {{
                        if (currentRoute) {{
                            if (map.getLayer('route')) map.removeLayer('route');
                            if (map.getSource('route')) map.removeSource('route');
                        }}
                        map.addSource('route', {{
                            type: 'geojson',
                            data: {{
                                type: 'Feature',
                                geometry: {{ type: 'LineString', coordinates: data.route }}
                            }}
                        }});
                        map.addLayer({{
                            id: 'route',
                            type: 'line',
                            source: 'route',
                            paint: {{ 'line-color': '#4285F4', 'line-width': 4 }}
                        }});
                        currentRoute = data.route;
                        document.getElementById('status').innerHTML = `🛣️ Itinéraire affiché`;
                    }}
                }})
                .catch(e => console.log(e));
        }}
        
        map.on('click', function(e) {{
            const lng = e.lngLat.lng;
            const lat = e.lngLat.lat;
            fetch(`/click?lat=${{lat}}&lng=${{lng}}`).catch(e => console.log(e));
            document.getElementById('status').innerHTML = `📍 ${{lat.toFixed(5)}}, ${{lng.toFixed(5)}}`;
            setTimeout(loadData, 500);
        }});
        
        document.getElementById('zoom-in').onclick = () => map.zoomIn();
        document.getElementById('zoom-out').onclick = () => map.zoomOut();
        document.getElementById('locate').onclick = () => {{
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(pos => {{
                    map.flyTo({{ center: [pos.coords.longitude, pos.coords.latitude], zoom: 15 }});
                }});
            }}
        }};
        document.getElementById('refresh').onclick = () => loadData();
        
        setInterval(loadData, 1000);
        loadData();
        
        console.log('Mapbox GL JS chargé');
    </script>
</body>
</html>'''
    
    def _create_browser_button(self):
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        self.layout.clear_widgets()
        
        info_label = Label(
            text="[b]🗺️ Carte ZAHEL[/b]\n\n"
                 "Cliquez sur le bouton ci-dessous\n"
                 "pour ouvrir la carte interactive\n\n"
                 "✓ Zoom / Déplacement\n"
                 "✓ Sélection des points\n"
                 "✓ Marqueurs en temps réel\n"
                 "✓ Itinéraire automatique",
            markup=True,
            halign='center',
            size_hint_y=0.5
        )
        
        btn_open = Button(
            text="🌍 OUVRIR LA CARTE",
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.5, 0.8, 1),
            font_size=18,
            bold=True
        )
        btn_open.bind(on_press=lambda x: webbrowser.open(self.map_url))
        
        self.layout.add_widget(info_label)
        self.layout.add_widget(btn_open)
    
    def _create_error_label(self):
        from kivy.uix.label import Label
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="❌ Erreur serveur", halign='center'))
    
    def _on_map_click(self, lat, lng):
        if self.on_click_callback:
            self.on_click_callback(lat, lng)
    
    def set_on_click(self, callback):
        self.on_click_callback = callback
        if self.server:
            self.server.set_on_click(callback)
    
    def add_marker(self, lat, lng, marker_type='depart'):
        if self.server:
            self.server.add_marker(lat, lng, marker_type)
            print(f"📍 Marqueur {marker_type} envoyé au serveur")
        else:
            print(f"⚠️ Serveur non disponible")

    def update_marker(self, lat, lng, marker_type='voiture'):
        if self.server:
            try:
                from mapbox_state import MapboxState
                MapboxState.markers = [m for m in MapboxState.markers if m.get('type') != marker_type]
                MapboxState.markers.append({'lat': lat, 'lng': lng, 'type': marker_type})
                print(f"🔄 Marqueur {marker_type} mis à jour à ({lat:.6f}, {lng:.6f})")
            except Exception as e:
                print(f"⚠️ Erreur update_marker: {e}")

    def draw_route(self, coordinates):
        print(f"🛣️ draw_route appelée avec {len(coordinates) if coordinates else 0} points")
    
        if coordinates and len(coordinates) >= 2:
            print(f"   Premier point: {coordinates[0]}")
            print(f"   Dernier point: {coordinates[-1]}")
            
            route_coords = [[coord[1], coord[0]] for coord in coordinates]
    
            if self.server and len(route_coords) >= 2:
                self.server.set_route(route_coords)
                print(f"🛣️ Itinéraire envoyé au serveur (format Mapbox)")
            else:
                print(f"⚠️ Impossible d'ajouter itinéraire")
        else:
            print(f"⚠️ Pas assez de points pour l'itinéraire")
    
    def clear(self):
        if self.server:
            self.server.clear()
    
    def center_on(self, lat, lng, zoom=None):
        print(f"📝 Centrer sur ({lat}, {lng})")
    
    def set_zoom(self, zoom):
        print(f"📝 Zoom {zoom}")

    def clear_markers_of_type(self, marker_type):
        if self.server:
            from mapbox_state import MapboxState
            MapboxState.markers = [m for m in MapboxState.markers if m.get('type') != marker_type]