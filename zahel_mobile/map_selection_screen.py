# map_selection_screen.py - Version ultra-simplifiée
import os
import webbrowser
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

from config.mapbox_config import MapboxConfig
from mapbox_server import MapboxServer


class MapSelectionScreen(Screen):
    """Écran de sélection de trajet - Version simplifiée"""
    
    def __init__(self, **kwargs):
        super(MapSelectionScreen, self).__init__(**kwargs)
        
        self.default_lat = -11.6980
        self.default_lng = 43.2560
        
        self.depart_coords = (self.default_lat, self.default_lng)
        self.arrivee_coords = None
        self.server = None
        self.map_url = None
        
        self.build_interface()
        Clock.schedule_once(self._start_server, 0.5)
        
        print("🗺️ MapSelectionScreen (version simplifiée) initialisée")
    
    def build_interface(self):
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        title = Label(
            text='🚕 ZAHEL',
            font_size='32sp',
            bold=True,
            size_hint_y=0.2,
            color=(0.2, 0.5, 0.8, 1)
        )
        
        info = Label(
            text='[b]Choisissez votre trajet sur la carte[/b]\n\n'
                 '1. Cliquez sur "Ouvrir la carte"\n'
                 '2. Sélectionnez votre DÉPART\n'
                 '3. Sélectionnez votre ARRIVÉE\n'
                 '4. Cliquez sur CONFIRMER\n\n'
                 '📍 Vous pouvez rechercher directement\n'
                 '   une adresse dans la carte Mapbox',
            markup=True,
            font_size='14sp',
            halign='center',
            valign='middle',
            size_hint_y=0.5
        )
        info.bind(size=info.setter('text_size'))
        
        self.btn_map = Button(
            text='🗺️ OUVRIR LA CARTE MAPBOX',
            size_hint_y=0.15,
            background_color=(0.2, 0.5, 0.8, 1),
            font_size='18sp',
            bold=True
        )
        self.btn_map.bind(on_press=self.open_map)
        
        self.btn_continue = Button(
            text='✅ CONTINUER VERS LE CHOIX DU VÉHICULE',
            size_hint_y=0.15,
            background_color=(0.1, 0.6, 0.2, 1),
            font_size='16sp',
            bold=True,
            disabled=True
        )
        self.btn_continue.bind(on_press=self.go_to_order)
        
        main_layout.add_widget(title)
        main_layout.add_widget(info)
        main_layout.add_widget(self.btn_map)
        main_layout.add_widget(self.btn_continue)
        
        self.add_widget(main_layout)
    
    def _start_server(self, dt):
        try:
            self.server = MapboxServer(port=8080)
            self.server.on_confirm = self.on_confirm
            
            html = self._generate_map_html()
            self.server.set_html(html)
            
            url = self.server.start()
            if url:
                self.map_url = url
                print(f"✅ Serveur Mapbox démarré: {url}")
        except Exception as e:
            print(f"⚠️ Erreur démarrage serveur: {e}")
    
    def _generate_map_html(self):
        html_path = os.path.join(os.path.dirname(__file__), 'carte.html')
    
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        
            html_content = html_content.replace('MAPBOX_TOKEN_PLACEHOLDER', MapboxConfig.ACCESS_TOKEN)
        
            print(f"✅ HTML chargé depuis {html_path}")
            return html_content
        
        except Exception as e:
            print(f"❌ Erreur lecture HTML: {e}")
            return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ZAHEL</title>
    <script src="https://api.mapbox.com/mapbox-gl-js/v3.5.0/mapbox-gl.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/v3.5.0/mapbox-gl.css" rel="stylesheet">
    <style>body{{margin:0;padding:0;}}#map{{position:absolute;top:0;bottom:0;width:100%;}}</style>
</head>
<body>
    <div id="map"></div>
    <script>
        mapboxgl.accessToken = '{MapboxConfig.ACCESS_TOKEN}';
        new mapboxgl.Map({{container:'map',style:'mapbox://styles/mapbox/streets-v12',center:[43.2560,-11.6980],zoom:13}}).addControl(new mapboxgl.NavigationControl());
    </script>
</body>
</html>'''
    
    def open_map(self, instance):
        if self.map_url:
            Clock.schedule_once(lambda dt: webbrowser.open(self.map_url), 0.5)
            print(f"🌐 Carte ouverte: {self.map_url}")
        else:
            print("❌ Serveur non disponible")
    
    def on_confirm(self, depart, arrivee):
        print(f"✅ Confirmation reçue")
        print(f"   Départ: ({depart['lat']:.6f}, {depart['lng']:.6f})")
        print(f"   Arrivée: ({arrivee['lat']:.6f}, {arrivee['lng']:.6f})")
        
        self.depart_coords = (depart['lat'], depart['lng'])
        self.arrivee_coords = (arrivee['lat'], arrivee['lng'])
        
        Clock.schedule_once(lambda dt: self.enable_continue_button(), 0)
    
    def enable_continue_button(self):
        self.btn_continue.disabled = False
        self.btn_continue.text = "✅ CONTINUER VERS LE CHOIX DU VÉHICULE"
    
    def go_to_order(self, instance):
        if not self.depart_coords or not self.arrivee_coords:
            print("❌ Pas de coordonnées disponibles")
            return
        
        print(f"🚕 Redirection vers écran de commande")
        
        if 'order_ride' not in self.manager.screen_names:
            from main import OrderRideScreen
            order_screen = OrderRideScreen(
                name='order_ride',
                depart_coords=self.depart_coords,
                arrivee_coords=self.arrivee_coords,
                destination="Destination sélectionnée sur la carte"
            )
            self.manager.add_widget(order_screen)
        else:
            order_screen = self.manager.get_screen('order_ride')
            order_screen.depart_coords = self.depart_coords
            order_screen.arrivee_coords = self.arrivee_coords
            order_screen.prices_updated = False
        
        self.manager.current = 'order_ride'
    
    def on_enter(self):
        print("🗺️ MapSelectionScreen activé")
        if not self.map_url:
            Clock.schedule_once(self._start_server, 0.1)