# map_selection_screen.py - Écran de sélection de trajet ZAHEL avec autocomplétion
import os
import sys
import webbrowser
import json
import urllib.request
import urllib.parse
import threading
import uuid 
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import ListProperty, StringProperty

from config.mapbox_config import MapboxConfig
from mapbox_server import MapboxServer


class SuggestionList(RecycleView):
    """Liste déroulante des suggestions"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        self.layout = RecycleBoxLayout(default_size=(None, 50), default_size_hint=(1, None), size_hint_y=None, height=500, orientation='vertical')
        self.add_widget(self.layout)
    
    def update_suggestions(self, suggestions):
        self.data = []
        for s in suggestions:
            self.data.append({
                'text': s.get('text', ''),
                'full_address': s.get('full_address', ''),
                'coords': s.get('coords', (0, 0))
            })
        self.refresh_from_data()


class MapSelectionScreen(Screen):
    """
    Écran de sélection de trajet ZAHEL - Version avec autocomplétion
    """
    
    def __init__(self, **kwargs):
        super(MapSelectionScreen, self).__init__(**kwargs)
        
        # État
        self.depart_coords = (-11.6980, 43.2560)  # Position par défaut (Moroni)
        self.arrivee_coords = None
        self.address_valid = False
        self.current_address = ""
        self.api_client = None
        self.server = None
        self.map_url = None
        self.suggestion_popup = None
        self.current_suggestions = []
        
        # Récupérer l'API client
        self._get_api_client()
        
        # Construire l'interface
        self.build_interface()
        
        # Démarrer le serveur Mapbox
        Clock.schedule_once(self._start_server, 0.5)

        # ⭐ Ajouter une session unique pour Search Box
        self.session_token = str(uuid.uuid4())

        # ⭐ Pour le debounce (éviter trop de requêtes)
        self.search_timer = None
        self.last_query = ""
        
        print("🗺️ MapSelectionScreen (version autocomplétion) initialisée")
    
    def _get_api_client(self):
        """Récupérer l'API client depuis l'application"""
        app = App.get_running_app()
        
        if hasattr(app, 'api_client') and app.api_client:
            self.api_client = app.api_client
            print("✅ API Client récupéré")
        else:
            try:
                from api.client import APIClient
                self.api_client = APIClient()
                print("✅ API Client créé")
            except Exception as e:
                print(f"⚠️ Impossible de créer API Client: {e}")
                self.api_client = None
    
    def build_interface(self):
        """Construire l'interface utilisateur"""
        main_layout = BoxLayout(orientation='vertical', spacing=0, padding=0)
        
        # En-tête
        header = BoxLayout(size_hint_y=0.08, padding=[15, 10, 15, 10], spacing=10)
        btn_back = Button(text='←', size_hint_x=0.1, font_size='20sp')
        btn_back.bind(on_press=self.go_back)
        lbl_title = Label(text='🚕 ZAHEL', font_size='18sp', bold=True, halign='center', color=COLORS['text_primary'])
        header.add_widget(btn_back)
        header.add_widget(lbl_title)
        header.add_widget(Label(size_hint_x=0.1))
        
        # Zone de recherche avec autocomplétion
        search_layout = BoxLayout(orientation='vertical', size_hint_y=0.3, padding=[15, 10, 15, 10], spacing=5)
        
        # Conteneur pour le champ de recherche et les suggestions
        self.search_container = BoxLayout(orientation='vertical', size_hint_y=1, spacing=0)
        
        # Champ de recherche
        self.txt_address = TextInput(
            hint_text='Entrez votre destination (ex: Aéroport Moroni)',
            multiline=False,
            font_size='16sp',
            background_color=(0.95, 0.95, 0.95, 1),
            size_hint_y=0.4
        )
        self.txt_address.bind(text=self.on_text_change)
        self.txt_address.bind(on_text_validate=self.validate_address)
        
        # Zone pour les suggestions (sera remplie dynamiquement)
        self.suggestions_box = BoxLayout(orientation='vertical', size_hint_y=0.6, spacing=0)
        
        self.search_container.add_widget(self.txt_address)
        self.search_container.add_widget(self.suggestions_box)
        
        # Indicateur de validation
        self.address_status = Label(
            text='❌ Adresse non validée',
            font_size='12sp',
            color=(0.8, 0.2, 0.2, 1),
            size_hint_y=0.15,
            halign='center'
        )
        
        search_layout.add_widget(self.search_container)
        search_layout.add_widget(self.address_status)
        
        # Zone d'information
        info_box = BoxLayout(orientation='vertical', size_hint_y=0.15, padding=[15, 5, 15, 5])
        self.lbl_depart = Label(
            text='📍 Départ: Votre position actuelle (Moroni, color=COLORS['text_primary'])',
            font_size='13sp',
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        self.lbl_arrivee = Label(
            text='🏁 Arrivée: Non sélectionnée',
            font_size='13sp',
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        info_box.add_widget(self.lbl_depart)
        info_box.add_widget(self.lbl_arrivee)
        
        # Boutons
        buttons_box = BoxLayout(orientation='vertical', size_hint_y=0.25, padding=[15, 5, 15, 15], spacing=15)
        
        self.btn_order = Button(
            text='🚕 COMMANDER UNE COURSE',
            size_hint_y=0.45,
            background_color=(0.1, 0.6, 0.2, 1),
            font_size='18sp',
            bold=True,
            disabled=True
        )
        self.btn_order.bind(on_press=self.command_ride)
        
        self.btn_map = Button(
            text='🗺️ SÉLECTIONNER SUR LA CARTE',
            size_hint_y=0.45,
            background_color=(0.2, 0.5, 0.8, 1),
            font_size='18sp',
            bold=True
        )
        self.btn_map.bind(on_press=self.open_map_selection)
        
        buttons_box.add_widget(self.btn_order)
        buttons_box.add_widget(self.btn_map)
        
        # Assemblage
        main_layout.add_widget(header)
        main_layout.add_widget(search_layout)
        main_layout.add_widget(info_box)
        main_layout.add_widget(buttons_box)
        
        self.add_widget(main_layout)
    
    def on_text_change(self, instance, value):
        """Quand le texte change, chercher des suggestions (avec délai)"""
    
        # Annuler la recherche précédente
        if self.search_timer:
            self.search_timer.cancel()
    
        if len(value) < 3:
            self.clear_suggestions()
            return
    
        # ⭐ Attendre 0.5 seconde après la dernière frappe
        from threading import Timer
        self.search_timer = Timer(0.5, self._do_search, [value])
        self.search_timer.start()

    def _do_search(self, query):
        """Lancer la recherche après le délai"""
        # Éviter les doublons
        if query == self.last_query:
            return
        self.last_query = query
    
        # Afficher un indicateur
        Clock.schedule_once(lambda dt: self._show_loading(), 0)
    
        # Lancer la recherche
        self.search_suggestions(query)

    def _show_loading(self):
        """Afficher un indicateur de recherche"""
        self.clear_suggestions()
        loading = Label(
            text='🔍 Recherche en cours...',
            size_hint_y=None,
            height=40,
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        self.suggestions_box.add_widget(loading)
    
    def search_suggestions(self, query):
        """Rechercher des suggestions d'adresses précises via Mapbox"""
        def search():
            try:
                encoded = urllib.parse.quote(query)
                # Ajouter types=poi pour avoir les points d'intérêt (boutiques, écoles, etc.)
                url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded}.json?access_token={MapboxConfig.ACCESS_TOKEN}&country=km&types=poi,address,place,locality,neighborhood&limit=10&autocomplete=true"
            
                print(f"🔍 Recherche précise: {query}")
            
                with urllib.request.urlopen(url, timeout=10) as response:
                    data = json.loads(response.read().decode())
                
                    features = data.get('features', [])
                    print(f"📡 {len(features)} résultats précis reçus")
                
                    suggestions = []
                    for feature in features:
                        coords = feature['center']  # [lng, lat]
                        place_name = feature.get('place_name', '')
                        properties = feature.get('properties', {})
                    
                        # Récupérer le nom précis (boutique, école, etc.)
                        name = feature.get('text', '')
                        category = properties.get('category', '')
                    
                        # Construire un nom plus lisible
                        if category:
                            display_name = f"{name} ({category}) - {place_name}"
                        else:
                            display_name = place_name
                    
                        suggestions.append({
                            'text': display_name[:60],
                            'full_address': place_name,
                            'coords': (coords[1], coords[0]),  # (lat, lng)
                            'name': name,
                            'category': category
                        })
                    
                        print(f"   → {display_name[:50]}")
                
                    Clock.schedule_once(lambda dt: self.display_suggestions(suggestions), 0)
                
            except Exception as e:
                print(f"❌ Erreur recherche suggestions: {e}")
    
        threading.Thread(target=search, daemon=True).start()

    def display_error_message(self):
        """Afficher un message d'erreur"""
        self.clear_suggestions()
        error_label = Label(
            text='⚠️ Problème de connexion\nVérifiez votre connexion Internet',
            size_hint_y=None,
            height=60,
            font_size='12sp',
            color=(0.8, 0.4, 0, 1),
            halign='center'
        )
        self.suggestions_box.add_widget(error_label)
    
    def display_suggestions(self, suggestions):
        """Afficher les suggestions d'adresses précises"""
        self.clear_suggestions()
    
        print(f"📋 Affichage de {len(suggestions)} suggestions précises")
    
        for s in suggestions:
            # Créer un layout horizontal pour chaque suggestion
            item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        
            # Icône selon le type
            icon = Label(text='📍', size_hint_x=0.1, font_size='20sp', color=COLORS['text_primary'])
        
            # Texte de l'adresse
            text_label = Label(
                text=s['text'],
                size_hint_x=0.8,
                font_size='13sp',
                halign='left',
                color=(0.1, 0.1, 0.1, 1),
                shorten=True,
                shorten_from='right'
            )
            text_label.bind(size=text_label.setter('text_size'))
        
            # Bouton de sélection
            select_btn = Button(text='✓', size_hint_x=0.1, background_color=(0.1, 0.7, 0.1, 1), font_size='16sp')
        
            # Stocker les données
            select_btn.full_address = s['full_address']
            select_btn.coords = s['coords']
            select_btn.bind(on_press=self.select_address_from_button)
        
            item_layout.add_widget(icon)
            item_layout.add_widget(text_label)
            item_layout.add_widget(select_btn)
        
            self.suggestions_box.add_widget(item_layout)
    
        if len(suggestions) == 0:
            no_result = Label(
                text='Aucune suggestion trouvée - Essayez une autre recherche',
                size_hint_y=None,
                height=40,
                font_size='12sp',
                color=(0.5, 0.5, 0.5, 1)
            )
            self.suggestions_box.add_widget(no_result)

    def _fallback_geocoding(self, query):
        """Fallback vers l'ancienne API Geocoding"""
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded}.json?access_token={MapboxConfig.ACCESS_TOKEN}&country=km&limit=5&autocomplete=true"
        
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                features = data.get('features', [])
            
                suggestions = []
                for feature in features:
                    coords = feature['center']
                    place_name = feature.get('place_name', '')
                    suggestions.append({
                        'text': place_name[:50],
                        'full_address': place_name,
                        'coords': (coords[1], coords[0]),
                        'mapbox_id': ''
                    })
            
                Clock.schedule_once(lambda dt: self.display_suggestions(suggestions), 0)
        except Exception as e:
            print(f"❌ Fallback échoué: {e}")

    def select_address_from_button(self, instance):
        """Sélectionner une adresse depuis un bouton de suggestion"""
        full_address = getattr(instance, 'full_address', '')
        coords = getattr(instance, 'coords', None)
    
        if coords:
            self._finalize_address_selection(full_address, coords)
        else:
            print(f"❌ Pas de coordonnées pour {full_address}")

    def _retrieve_coordinates(self, mapbox_id, full_address):
        """Récupérer les coordonnées précises via Search Box Retrieve"""
        def retrieve():
            try:
                url = f"https://api.mapbox.com/search/searchbox/v1/retrieve/{mapbox_id}?access_token={MapboxConfig.ACCESS_TOKEN}&session_token={self.session_token}"
            
                with urllib.request.urlopen(url, timeout=10) as response:
                    data = json.loads(response.read().decode())
                
                    feature = data.get('features', [{}])[0]
                    geometry = feature.get('geometry', {})
                    coordinates = geometry.get('coordinates', [0, 0])  # [lng, lat]
                
                    if len(coordinates) == 2:
                        lat, lng = coordinates[1], coordinates[0]
                        Clock.schedule_once(lambda dt: self._finalize_address_selection(full_address, (lat, lng)), 0)
                    else:
                        print(f"❌ Pas de coordonnées pour {full_address}")
                    
            except Exception as e:
                print(f"❌ Erreur retrieve: {e}")
    
        threading.Thread(target=retrieve, daemon=True).start()

    def _finalize_address_selection(self, full_address, coords):
        """Finaliser la sélection d'adresse avec coordonnées"""
        self.txt_address.text = full_address
        self.arrivee_coords = coords
        self.current_address = full_address
        self.address_valid = True
    
        self.address_status.text = f'✅ Adresse validée: {full_address[:40]}'
        self.address_status.color = (0.1, 0.7, 0.1, 1)
        self.lbl_arrivee.text = f'🏁 Arrivée: {full_address[:50]}'
        self.btn_order.disabled = False
    
        self.clear_suggestions()
        print(f"✅ Adresse sélectionnée: {full_address} -> {coords}")
    
    def clear_suggestions(self):
        """Effacer les suggestions"""
        self.suggestions_box.clear_widgets()
    
    def select_address(self, full_address, coords):
        """Sélectionner une adresse depuis les suggestions"""
        self.txt_address.text = full_address
        self.arrivee_coords = coords
        self.current_address = full_address
        self.address_valid = True
        
        self.address_status.text = f'✅ Adresse validée: {full_address[:40]}'
        self.address_status.color = (0.1, 0.7, 0.1, 1)
        self.lbl_arrivee.text = f'🏁 Arrivée: {full_address[:50]}'
        self.btn_order.disabled = False
        
        self.clear_suggestions()
        print(f"✅ Adresse sélectionnée: {full_address} -> {coords}")
    
    def validate_address(self, instance):
        """Valider l'adresse saisie manuellement"""
        address = self.txt_address.text.strip()
        
        if not address:
            self.address_status.text = '❌ Veuillez saisir une adresse'
            self.address_status.color = (0.8, 0.2, 0.2, 1)
            self.address_valid = False
            self.btn_order.disabled = True
            return
        
        self.address_status.text = '🔄 Vérification de l\'adresse...'
        self.address_status.color = (0.2, 0.5, 0.8, 1)
        
        def search():
            try:
                encoded = urllib.parse.quote(address)
                url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded}.json?access_token={MapboxConfig.ACCESS_TOKEN}&country=km&limit=1"
                
                with urllib.request.urlopen(url, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    
                    if data.get('features') and len(data['features']) > 0:
                        feature = data['features'][0]
                        coords = feature['center']
                        place_name = feature.get('place_name', address)
                        
                        self.arrivee_coords = (coords[1], coords[0])
                        self.current_address = place_name
                        self.address_valid = True
                        
                        Clock.schedule_once(lambda dt: self._update_ui_after_validation(place_name, coords[1], coords[0]), 0)
                    else:
                        Clock.schedule_once(lambda dt: self._update_ui_validation_failed(), 0)
            except Exception as e:
                print(f"Erreur géocodage: {e}")
                Clock.schedule_once(lambda dt: self._update_ui_validation_failed(), 0)
        
        threading.Thread(target=search, daemon=True).start()
    
    def _update_ui_after_validation(self, place_name, lat, lng):
        """Mettre à jour l'interface après validation réussie"""
        self.address_status.text = f'✅ Adresse validée: {place_name[:40]}'
        self.address_status.color = (0.1, 0.7, 0.1, 1)
        self.lbl_arrivee.text = f'🏁 Arrivée: {place_name[:50]}'
        self.btn_order.disabled = False
        print(f"✅ Adresse validée: {place_name} ({lat:.6f}, {lng:.6f})")
    
    def _update_ui_validation_failed(self):
        """Mettre à jour l'interface après échec de validation"""
        self.address_status.text = '❌ Adresse non trouvée aux Comores'
        self.address_status.color = (0.8, 0.2, 0.2, 1)
        self.address_valid = False
        self.arrivee_coords = None
        self.btn_order.disabled = True
    
    def command_ride(self, instance):
        """Commander une course avec l'adresse validée"""
        if not self.address_valid or not self.arrivee_coords:
            self.address_status.text = '❌ Veuillez saisir une adresse valide'
            self.address_status.color = (0.8, 0.2, 0.2, 1)
            return
        
        print(f"🚕 Commande directe:")
        print(f"   Départ: {self.depart_coords}")
        print(f"   Arrivée: {self.arrivee_coords}")
        print(f"   Adresse: {self.current_address}")
        
        # Ouvrir la carte avec l'itinéraire pré-rempli
        self._open_map_with_route(self.depart_coords, self.arrivee_coords)
    
    def open_map_selection(self, instance):
        """Ouvrir la carte pour sélection manuelle"""
        print("🗺️ Ouverture carte pour sélection manuelle")
        self._open_map_with_route(None, None)
    
    def _open_map_with_route(self, start_coords, end_coords):
        """Ouvrir la carte dans le navigateur avec itinéraire"""
        if not self.map_url:
            self.address_status.text = '⚠️ Serveur carte non disponible'
            return
        
        # Si on a un itinéraire pré-rempli, le passer en paramètre
        if start_coords and end_coords:
            url_with_coords = f"{self.map_url}?depart_lat={start_coords[0]}&depart_lng={start_coords[1]}&arrivee_lat={end_coords[0]}&arrivee_lng={end_coords[1]}"
            webbrowser.open(url_with_coords)
        else:
            webbrowser.open(self.map_url)
        
        print(f"🌐 Carte ouverte: {self.map_url}")
    
    def _start_server(self, dt):
        """Démarrer le serveur local pour la carte"""
        try:
            self.server = MapboxServer(port=8080)
            self.server.set_on_click(self._on_map_click)
            self.server.on_confirm = self.on_confirm
            
            html = self._generate_full_html()
            self.server.set_html(html)
            
            url = self.server.start()
            if url:
                self.map_url = url
                print(f"✅ Serveur Mapbox démarré: {url}")
        except Exception as e:
            print(f"⚠️ Erreur démarrage serveur: {e}")
    
    def _generate_full_html(self):
        """Générer le HTML en lisant un fichier externe"""
        html_path = os.path.join(os.path.dirname(__file__), 'carte.html')
        
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            html_content = html_content.replace('MAPBOX_TOKEN_PLACEHOLDER', MapboxConfig.ACCESS_TOKEN)
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
    
    def _on_map_click(self, lat, lng):
        print(f"📍 Clic carte: ({lat:.6f}, {lng:.6f})")
    
    def on_confirm(self, depart, arrivee):
        """Callback quand l'utilisateur confirme sur la carte"""
        print(f"✅ Confirmation reçue - Départ: {depart}, Arrivée: {arrivee}")
        
        self.depart_coords = (depart['lat'], depart['lng'])
        self.arrivee_coords = (arrivee['lat'], arrivee['lng'])
        
        Clock.schedule_once(lambda dt: self.go_to_order_screen(), 0.5)
    
    def go_to_order_screen(self):
        """Aller à l'écran de commande avec les coordonnées"""
        if not self.depart_coords or not self.arrivee_coords:
            print("❌ Pas de coordonnées disponibles")
            return
        
        print(f"🚕 Redirection vers écran de commande")
        print(f"   Départ: {self.depart_coords}")
        print(f"   Arrivée: {self.arrivee_coords}")
        
        if 'order_ride' not in self.manager.screen_names:
            from main import OrderRideScreen
            order_screen = OrderRideScreen(
                name='order_ride',
                depart_coords=self.depart_coords,
                arrivee_coords=self.arrivee_coords,
                destination=self.current_address if hasattr(self, 'current_address') else "Destination"
            )
            self.manager.add_widget(order_screen)
        else:
            order_screen = self.manager.get_screen('order_ride')
            order_screen.depart_coords = self.depart_coords
            order_screen.arrivee_coords = self.arrivee_coords
            if hasattr(self, 'current_address'):
                order_screen.destination = self.current_address
            order_screen.prices_updated = False
        
        self.manager.current = 'order_ride'
    
    def go_back(self, instance):
        self.manager.current = 'home'
    
    def on_enter(self):
        print("🗺️ MapSelectionScreen activé")
        if not self.map_url:
            Clock.schedule_once(self._start_server, 0.1)