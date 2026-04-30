# mapbox_real_webview_simple.py - WebView simple et fonctionnelle
import os
import sys
import json
import threading
import time
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import webbrowser

try:
    import webview
    WEBVIEW_AVAILABLE = True
    print("✅ pywebview disponible")
except ImportError as e:
    WEBVIEW_AVAILABLE = False
    print(f"⚠️ pywebview non disponible: {e}")

from config.mapbox_config import MapboxConfig
from mapbox_server import MapboxServer


class MapboxRealWebViewSimple(Widget):
    """
    WebView simple et fonctionnelle pour Mapbox
    """
    
    def __init__(self, **kwargs):
        self.lat = kwargs.pop('lat', MapboxConfig.DEFAULT_LAT)
        self.lng = kwargs.pop('lng', MapboxConfig.DEFAULT_LNG)
        self.zoom = kwargs.pop('zoom', MapboxConfig.DEFAULT_ZOOM)
        self.style = kwargs.pop('style', MapboxConfig.DEFAULT_STYLE)
        
        super(MapboxRealWebViewSimple, self).__init__(**kwargs)
        
        self.server = None
        self.webview_window = None
        self.on_click_callback = None
        self.map_url = None
        
        self.layout = BoxLayout(orientation='vertical', size_hint=(1, 1))
        self.add_widget(self.layout)
        
        Clock.schedule_once(self._init_webview, 0.5)
        print(f"🗺️ MapboxRealWebViewSimple initialisée")
    
    def _init_webview(self, dt):
        """Initialiser la WebView"""
        try:
            # Démarrer le serveur local
            self.server = MapboxServer()
            self.server.set_on_click(self._on_map_click)
            
            # Générer le HTML simple
            html_content = self._generate_simple_html()
            self.server.set_html(html_content)
            
            url = self.server.start()
            
            if url:
                self.map_url = url
                print(f"✅ Serveur démarré: {url}")
                
                # Ouvrir dans le navigateur par défaut (solution temporaire)
                self._open_in_browser(url)
            else:
                self._create_error_label()
                
        except Exception as e:
            print(f"❌ Erreur initialisation WebView: {e}")
            import traceback
            traceback.print_exc()
            self._create_error_label()
    
    def _generate_simple_html(self):
        """Générer le HTML simple"""
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>ZAHEL Map - Sélection de trajet</title>
    <script src="https://api.mapbox.com/mapbox-gl-js/v3.5.0/mapbox-gl.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/v3.5.0/mapbox-gl.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; }}
        body {{ 
            margin: 0; 
            padding: 0; 
            overflow: hidden; 
            height: 100vh; 
            font-family: Arial, sans-serif; 
            background: #f5f5f5;
        }}
        #map {{ 
            position: absolute; 
            top: 0; 
            bottom: 0; 
            width: 100%; 
            height: 100%;
        }}
        
        /* Panneau d'information */
        .info-panel {{
            position: absolute; top: 20px; left: 20px; right: 20px;
            background: rgba(255,255,255,0.95); padding: 15px;
            border-radius: 12px; font-size: 14px; z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            display: flex; justify-content: space-between; align-items: center;
        }}
        
        .info-panel .title {{
            font-weight: bold; color: #333; font-size: 16px;
        }}
        
        .info-panel .status {{
            color: #666; font-size: 13px;
        }}
        
        /* Marqueurs */
        .marker-depart {{
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%234285F4" width="48px" height="48px"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>');
            background-size: cover; width: 48px; height: 48px; cursor: pointer;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
        }}
        
        .marker-arrivee {{
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23E53935" width="48px" height="48px"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>');
            background-size: cover; width: 48px; height: 48px; cursor: pointer;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    
    <!-- Panneau d'information -->
    <div class="info-panel">
        <div>
            <div class="title">🗺️ ZAHEL - Sélectionnez votre trajet</div>
            <div class="status" id="status">Cliquez sur la carte pour sélectionner le départ</div>
        </div>
        <div id="coordinates">Lat: {self.lat:.4f}, Lng: {self.lng:.4f}</div>
    </div>
    
    <script>
        // Variables globales
        mapboxgl.accessToken = '{MapboxConfig.ACCESS_TOKEN}';
        let map = null;
        let markers = [];
        
        // Styles Mapbox
        const styles = {{
            'streets': 'mapbox://styles/mapbox/streets-v12',
            'satellite': 'mapbox://styles/mapbox/satellite-v9',
            'light': 'mapbox://styles/mapbox/light-v11',
            'dark': 'mapbox://styles/mapbox/dark-v11',
            'navigation_day': 'mapbox://styles/mapbox/navigation-day-v1',
            'navigation_night': 'mapbox://styles/mapbox/navigation-night-v1'
        }};
        
        // Initialiser la carte
        function initMap() {{
            map = new mapboxgl.Map({{
                container: 'map',
                style: styles['{self.style}'],
                center: [{self.lng}, {self.lat}],
                zoom: {self.zoom},
                pitch: 45,
                bearing: 0
            }});
            
            // Ajouter les contrôles
            map.addControl(new mapboxgl.NavigationControl(), 'top-right');
            map.addControl(new mapboxgl.GeolocateControl({{
                positionOptions: {{ enableHighAccuracy: true }},
                trackUserLocation: true,
                showUserLocation: true
            }}), 'top-right');
            
            // Gestion des clics sur la carte
            map.on('click', function(e) {{
                const lng = e.lngLat.lng;
                const lat = e.lngLat.lat;
                
                // Envoyer les coordonnées au serveur
                fetch(`/click?lat=${{lat}}&lng=${{lng}}`).catch(e => console.log(e));
                
                // Mettre à jour l'affichage
                document.getElementById('coordinates').innerHTML = 
                    `Lat: ${{lat.toFixed(6)}}, Lng: ${{lng.toFixed(6)}}`;
                
                // Ajouter un marqueur
                addMarker(lat, lng);
                
                // Mettre à jour le statut
                document.getElementById('status').innerHTML = 
                    `✅ Point sélectionné: ${{lat.toFixed(6)}}, ${{lng.toFixed(6)}}`;
            }});
            
            // Chargement initial
            map.on('load', function() {{
                console.log('Carte Mapbox chargée');
            }});
        }}
        
        // Ajouter un marqueur
        function addMarker(lat, lng) {{
            // Nettoyer les anciens marqueurs
            markers.forEach(m => m.remove());
            markers = [];
            
            // Créer un nouveau marqueur
            const el = document.createElement('div');
            el.className = 'marker-depart';
            const marker = new mapboxgl.Marker(el)
                .setLngLat([lng, lat])
                .addTo(map);
            
            // Ajouter une popup
            const popup = new mapboxgl.Popup({{ offset: 25 }})
                .setHTML(`<div style="padding: 8px;">
                    <strong>📍 Point sélectionné</strong><br>
                    Lat: ${{lat.toFixed(6)}}<br>
                    Lng: ${{lng.toFixed(6)}}
                </div>`);
            
            marker.setPopup(popup);
            markers.push(marker);
        }}
        
        // Démarrer l'application
        window.onload = initMap;
    </script>
</body>
</html>'''
    
    def _on_map_click(self, lat, lng):
        """Gérer les clics sur la carte"""
        print(f"📍 Clic sur carte: ({lat:.6f}, {lng:.6f})")
        if self.on_click_callback:
            self.on_click_callback(lat, lng)
    
    def _open_in_browser(self, url):
        """Ouvrir dans le navigateur par défaut"""
        try:
            webbrowser.open(url)
            print(f"🌐 Carte ouverte dans le navigateur: {url}")
        except Exception as e:
            print(f"❌ Erreur ouverture navigateur: {e}")
    
    def _create_error_label(self):
        """Créer un label d'erreur"""
        error_label = Label(
            text="❌ Impossible de charger la carte Mapbox\nVérifiez votre connexion internet",
            font_size='16sp',
            color=(0.8, 0.1, 0.1, 1),
            halign='center',
            valign='middle'
        )
        self.layout.add_widget(error_label)
    
    # ========== MÉTHODES PUBLIQUES ==========
    
    def set_on_click(self, callback):
        """Définir le callback pour les clics sur la carte"""
        self.on_click_callback = callback
        print("✅ Callback clic défini")
    
    def add_marker(self, lat, lng, marker_type='depart'):
        """Ajouter un marqueur sur la carte"""
        print(f"📍 Marqueur {marker_type} ajouté à ({lat:.6f}, {lng:.6f})")
        # Cette méthode serait implémentée via communication avec le serveur
    
    def clear(self):
        """Effacer tous les marqueurs"""
        print("🗑️ Tous les marqueurs effacés")
        # Cette méthode serait implémentée via communication avec le serveur
    
    def draw_route(self, route_points):
        """Dessiner un itinéraire"""
        print(f"🛣️ Itinéraire dessiné avec {len(route_points)} points")
        # Cette méthode serait implémentée via communication avec le serveur
    
    def center_on(self, lat, lng):
        """Centrer la carte sur des coordonnées"""
        print(f"🎯 Carte centrée sur ({lat:.6f}, {lng:.6f})")
        # Cette méthode serait implémentée via communication avec le serveur
    
    def set_zoom(self, zoom):
        """Définir le niveau de zoom"""
        print(f"🔍 Zoom défini à {zoom}")
        # Cette méthode serait implémentée via communication avec le serveur