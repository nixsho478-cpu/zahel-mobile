# tracking_mapbox.py - Écran de suivi client avec Mapbox (AVEC DÉTECTION ANNULATION)
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.app import App
import math
import webbrowser


class DriverTrackingScreenMapbox(Screen):
    """
    Écran de suivi du conducteur pour le client avec Mapbox
    Interface complète avec TOUTES les informations
    """
    
    def __init__(self, driver=None, destination="", price=0, course_code=None, 
                 depart_coords=None, arrivee_coords=None, **kwargs):
        super(DriverTrackingScreenMapbox, self).__init__(**kwargs)
        
        # ⭐ Initialiser self.driver avec TOUTES les clés par défaut
        self.driver = {
            'nom': 'Conducteur',
            'immatricule': '---',
            'vehicule': 'Véhicule',
            'marque': '',
            'modele': '',
            'couleur': '',
            'plaque': 'XX-000-XX',
            'note': 5.0,
            'telephone': '',
            'prix': price,
            'eta': '~4 min'
        }
        
        # ⭐ Mettre à jour avec les données du driver si fournies
        if driver:
            if isinstance(driver, dict):
                self.driver['nom'] = driver.get('nom') or driver.get('name', self.driver['nom'])
                self.driver['immatricule'] = driver.get('immatricule', self.driver['immatricule'])
                self.driver['vehicule'] = driver.get('vehicule') or driver.get('vehicle', self.driver['vehicule'])
                self.driver['marque'] = driver.get('marque_vehicule', self.driver['marque'])
                self.driver['modele'] = driver.get('modele_vehicule', self.driver['modele'])
                self.driver['couleur'] = driver.get('couleur_vehicule', self.driver['couleur'])
                self.driver['plaque'] = driver.get('plaque_immatriculation') or driver.get('plaque') or driver.get('plate', self.driver['plaque'])
                self.driver['note'] = driver.get('note') or driver.get('rating', self.driver['note'])
                self.driver['telephone'] = driver.get('telephone') or driver.get('phone', self.driver['telephone'])
                self.driver['prix'] = driver.get('prix') or driver.get('price', self.driver['prix'])
                self.driver['eta'] = driver.get('eta', self.driver['eta'])
        
        self.destination = destination
        self.price = price
        self.course_code = course_code
        
        # Stocker les coordonnées pour le suivi
        self.depart_coords = depart_coords
        self.destination_coords = arrivee_coords
        
        self.tracking_enabled = True
        self.route_drawn = False
        self.static_markers_added = False
        self.current_phase = None
        self.current_map_url = None
        self.map_already_opened = False
        self.annulation_popup_shown = False  # ⭐ Pour éviter les popups multiples
        
        self.build_interface()
        
        # Démarrer les mises à jour temps réel (toutes les 3 secondes)
        Clock.schedule_interval(self.update_tracking, 3)
        print(f"✅ DriverTrackingScreenMapbox initialisé - Prix: {self.price} KMF")
    
    def build_interface(self):
        """Construire l'interface complète avec toutes les infos"""
        main_layout = BoxLayout(orientation='vertical', spacing=0, padding=[10, 5, 10, 5])
        
        # ========== EN-TÊTE ==========
        header = BoxLayout(size_hint=(1, 0.05))
        header.add_widget(Label(
            text='[b]🚗 ZAHEL - Suivi[/b]',
            markup=True,
            font_size='16sp',
            halign='center'
        ))
        
        # ========== BOUTON CARTE (PRINCIPAL) ==========
        self.btn_view_map = Button(
            text='[size=18]🗺️ OUVRIR LA CARTE DE SUIVI[/size]',
            markup=True,
            size_hint=(1, 0.10),
            background_color=(0.2, 0.6, 0.4, 1),
            bold=True
        )
        self.btn_view_map.bind(on_press=self.open_tracking_map_manual)
        
        # ========== STATUT ==========
        self.lbl_status = Label(
            text='[size=14][color=FF9900]🚗 Conducteur en approche[/color][/size]',
            markup=True,
            halign='center',
            size_hint=(1, 0.05)
        )
        
        # ========== INFORMATIONS CONDUCTEUR (TOUTES LES INFOS) ==========
        driver_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.28),
            spacing=3,
            padding=[10, 2]
        )
        
        # Ligne 1: Nom et note
        self.lbl_name = Label(
            text=f'[size=16][b]{self.driver["nom"]}[/b][/size]  ★ {self.driver["note"]}',
            markup=True,
            halign='left',
            size_hint=(1, 0.15)
        )
        
        # Ligne 2: Immatricule conducteur
        self.lbl_immatricule = Label(
            text=f'🆔 [b]{self.driver["immatricule"]}[/b]',
            markup=True,
            halign='left',
            size_hint=(1, 0.12),
            color=(0.3, 0.3, 0.8, 1)
        )
        
        # Ligne 3: Véhicule complet
        vehicule_complet = f"{self.driver['marque']} {self.driver['modele']}".strip()
        if self.driver['couleur']:
            vehicule_complet += f" ({self.driver['couleur']})"
        if not vehicule_complet:
            vehicule_complet = self.driver['vehicule']
        
        self.lbl_vehicle = Label(
            text=f'🚗 {vehicule_complet}',
            markup=True,
            halign='left',
            size_hint=(1, 0.12)
        )
        
        # Ligne 4: Plaque d'immatriculation
        self.lbl_plate = Label(
            text=f'[size=16]🚘 Plaque:[/size] [size=20][b][color=0088CC]{self.driver["plaque"]}[/color][/b][/size]',
            markup=True,
            halign='center',
            size_hint=(1, 0.18)
        )
        
        # Ligne 5: ETA
        self.lbl_eta = Label(
            text=f'⏱️ Arrivée estimée: [b]{self.driver["eta"]}[/b]',
            markup=True,
            halign='left',
            size_hint=(1, 0.15),
            color=(0.2, 0.5, 0.8, 1)
        )
        
        driver_box.add_widget(self.lbl_name)
        driver_box.add_widget(self.lbl_immatricule)
        driver_box.add_widget(self.lbl_vehicle)
        driver_box.add_widget(self.lbl_plate)
        driver_box.add_widget(self.lbl_eta)
        
        # ========== PROGRESSION ==========
        progress_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.06),
            padding=[10, 0]
        )
        self.progress_bar = ProgressBar(max=100, value=25)
        progress_box.add_widget(self.progress_bar)
        
        # ========== INFORMATIONS COURSE ==========
        course_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.10),
            padding=[10, 2]
        )
        
        dest_text = self.destination[:35] + "..." if len(self.destination) > 35 else self.destination
        self.lbl_dest = Label(
            text=f'📍 {dest_text}',
            markup=True,
            halign='left',
            size_hint=(1, 0.5)
        )
        
        # PRIX BIEN VISIBLE
        self.lbl_price = Label(
            text=f'💰 [size=18][b]{self.price} KMF[/b][/size]',
            markup=True,
            halign='left',
            size_hint=(1, 0.5),
            color=(0.2, 0.6, 0.2, 1)
        )
        
        course_box.add_widget(self.lbl_dest)
        course_box.add_widget(self.lbl_price)
        
        # ========== BOUTONS D'ACTION ==========
        actions_section = GridLayout(
            cols=3,
            rows=1,
            size_hint=(1, 0.10),
            spacing=8,
            padding=[10, 2]
        )
        
        btn_contact = Button(
            text='📞 Appeler',
            background_color=(0.2, 0.5, 0.8, 1),
            bold=True
        )
        btn_contact.bind(on_press=self.contact_driver)
        
        btn_safety = Button(
            text='🛡️ Sécurité',
            background_color=(0.8, 0.5, 0.2, 1),
            bold=True
        )
        btn_safety.bind(on_press=self.show_safety)
        
        btn_cancel = Button(
            text='❌ Annuler',
            background_color=(0.8, 0.2, 0.2, 1),
            bold=True
        )
        btn_cancel.bind(on_press=self.cancel_ride)
        
        actions_section.add_widget(btn_contact)
        actions_section.add_widget(btn_safety)
        actions_section.add_widget(btn_cancel)
        
        # ========== ASSEMBLAGE ==========
        main_layout.add_widget(header)
        main_layout.add_widget(self.btn_view_map)
        main_layout.add_widget(self.lbl_status)
        main_layout.add_widget(driver_box)
        main_layout.add_widget(progress_box)
        main_layout.add_widget(course_box)
        main_layout.add_widget(actions_section)
        
        # Espaceur
        main_layout.add_widget(Label(size_hint=(1, 0.05)))
        
        self.add_widget(main_layout)
        
        # DEBUG
        print(f"🔧 Interface construite - Prix: {self.price} KMF")
    
    def update_tracking(self, dt=None):
        """Mettre à jour le suivi depuis l'API - DONNÉES RÉELLES"""
        if not self.tracking_enabled or not self.course_code:
            return
    
        app = App.get_running_app()
    
        if hasattr(app, 'api_client') and app.api_client:
            try:
                result = app.api_client.get_course_status(self.course_code)
            except Exception as e:
                return
        
            if result and result.get('success'):
                course = result.get('course', {})
                statut = course.get('statut', '')
            
                # ⭐⭐⭐ DÉTECTER L'ANNULATION OU LE REFUS ⭐⭐⭐
                if statut == 'annulee':
                    annule_par = course.get('annule_par', 'inconnu')
                    print(f"❌ Course annulée - par: {annule_par}")
                    self.tracking_enabled = False
                    
                    # Afficher un popup une seule fois
                    if not self.annulation_popup_shown:
                        self.annulation_popup_shown = True
                        
                        if annule_par == 'conducteur':
                            self.show_conducteur_refus_popup()
                        else:
                            self.show_annulation_popup()
                    
                    # Retour à la recherche après 3 secondes
                    Clock.schedule_once(lambda dt: self.return_to_search(), 3)
                    return
                
                # Sauvegarder la phase précédente
                phase_precedente = self.current_phase
            
                # Mettre à jour le statut
                if statut == 'en_recherche':
                    self.lbl_status.text = '[size=14][color=FF9900]🔍 Recherche conducteur...[/color][/size]'
                    self.progress_bar.value = 10
                elif statut == 'acceptee':
                    self.lbl_status.text = '[size=14][color=FF9900]🚗 Conducteur en approche[/color][/size]'
                    self.progress_bar.value = 30
                    self.current_phase = 'approche'
                elif statut == 'en_cours':
                    self.progress_bar.value = 60
                    self.lbl_status.text = '[size=14][color=00CC00]🛣️ En route vers destination[/color][/size]'
                    self.current_phase = 'course'
                
                    if phase_precedente != 'course':
                        print("🔄 Phase changée: approche → course - La carte se mettra à jour automatiquement")
                elif statut == 'terminee':
                    self.lbl_status.text = '[size=14][color=00CC00]✅ Course terminée[/color][/size]'
                    self.progress_bar.value = 100
                    Clock.schedule_once(lambda dt: self.go_home(), 2)
                    return
                
                # METTRE À JOUR LE PRIX
                prix_api = course.get('prix_convenu') or course.get('prix_final') or course.get('prix_total')
                if prix_api:
                    self.price = float(prix_api)
                    self.lbl_price.text = f'💰 [size=18][b]{int(self.price)} KMF[/b][/size]'
                
                # METTRE À JOUR TOUTES LES INFOS CONDUCTEUR
                conducteur = course.get('conducteur', {})
                if conducteur:
                    nom = conducteur.get('nom', self.driver.get('nom', 'Conducteur'))
                    note = conducteur.get('note_moyenne', self.driver.get('note', 5.0))
                    self.lbl_name.text = f'[size=16][b]{nom}[/b][/size]  ★ {note}'
                    
                    immatricule = conducteur.get('immatricule', self.driver.get('immatricule', '---'))
                    self.lbl_immatricule.text = f'🆔 [b]{immatricule}[/b]'
                    self.driver['immatricule'] = immatricule
                    
                    marque = conducteur.get('marque_vehicule', '')
                    modele = conducteur.get('modele_vehicule', '')
                    couleur = conducteur.get('couleur_vehicule', '')
                    
                    self.driver['marque'] = marque
                    self.driver['modele'] = modele
                    self.driver['couleur'] = couleur
                    
                    vehicule_complet = f"{marque} {modele}".strip()
                    if couleur:
                        vehicule_complet += f" ({couleur})"
                    if vehicule_complet:
                        self.lbl_vehicle.text = f'🚗 {vehicule_complet}'
                    
                    plaque = conducteur.get('plaque_immatriculation') or conducteur.get('plaque', 'XX-000-XX')
                    self.lbl_plate.text = f'[size=16]🚘 Plaque:[/size] [size=20][b][color=0088CC]{plaque}[/color][/b][/size]'
                    self.driver['plaque'] = plaque
                    
                    telephone = conducteur.get('telephone', '')
                    if telephone:
                        self.driver['telephone'] = telephone
                    
                    lat = conducteur.get('latitude')
                    lng = conducteur.get('longitude')
                    
                    if lat and lng:
                        if self.current_phase == 'approche' and self.depart_coords:
                            distance = self.haversine_distance(lat, lng, 
                                self.depart_coords[0], self.depart_coords[1])
                            eta = max(1, int(distance * 4))
                            self.lbl_eta.text = f'⏱️ Arrivée estimée: [b]~{eta} min[/b]'
                        elif self.current_phase == 'course' and self.destination_coords:
                            distance = self.haversine_distance(lat, lng, 
                                self.destination_coords[0], self.destination_coords[1])
                            eta = max(1, int(distance * 4))
                            self.lbl_eta.text = f'⏱️ Arrivée estimée: [b]~{eta} min[/b]'
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculer la distance en km entre deux points GPS"""
        R = 6371
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    # ⭐⭐⭐ NOUVELLE MÉTHODE : POPUP D'ANNULATION ⭐⭐⭐
    def show_annulation_popup(self):
        """Afficher un popup d'annulation"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        content.add_widget(Label(
            text="❌ COURSE ANNULÉE",
            font_size='22sp',
            bold=True,
            color=(1, 0, 0, 1),
            size_hint_y=None,
            height=40
        ))
        
        content.add_widget(Label(
            text="Le conducteur a annulé la course.\n\n"
                 "Vous allez être redirigé vers l'accueil\n"
                 "pour rechercher un autre conducteur.",
            halign='center',
            font_size='16sp',
            size_hint_y=None,
            height=80
        ))
        
        btn_ok = Button(
            text="OK",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 0.2, 1)
        )
        
        popup = Popup(
            title='Annulation',
            content=content,
            size_hint=(0.8, 0.45),
            auto_dismiss=False
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        content.add_widget(btn_ok)
        
        popup.open()
        print("📢 Popup d'annulation affiché")
    
    def _get_map_url(self):
        """Générer l'URL de la carte"""
        if not self.course_code:
            return None
        
        depart_lat = self.depart_coords[0] if self.depart_coords else -11.698
        depart_lng = self.depart_coords[1] if self.depart_coords else 43.256
        arrivee_lat = self.destination_coords[0] if self.destination_coords else -11.71
        arrivee_lng = self.destination_coords[1] if self.destination_coords else 43.265
        
        return (f"http://localhost:8080/suivi?"
                f"course={self.course_code}"
                f"&depart_lat={depart_lat}"
                f"&depart_lng={depart_lng}"
                f"&arrivee_lat={arrivee_lat}"
                f"&arrivee_lng={arrivee_lng}")
    
    def open_tracking_map_manual(self, instance):
        """Ouvrir la carte de suivi manuellement (bouton)"""
        url = self._get_map_url()
        if url:
            webbrowser.open(url)
            print(f"🗺️ Carte de suivi ouverte manuellement")
    
    def open_tracking_map_auto(self):
        """Ouvrir la carte de suivi automatiquement (une seule fois)"""
        if self.map_already_opened:
            return
        
        url = self._get_map_url()
        if url:
            webbrowser.open(url)
            self.map_already_opened = True
            print(f"🗺️ Carte de suivi ouverte automatiquement")
    
    def contact_driver(self, instance):
        """Contacter le conducteur"""
        if self.driver.get('telephone'):
            webbrowser.open(f"tel:{self.driver['telephone']}")
        else:
            self.show_popup("Info", "Numéro du conducteur non disponible")
    
    def show_safety(self, instance):
        """Afficher les infos de sécurité"""
        self.show_popup(
            "Sécurité ZAHEL",
            "• Conducteur vérifié\n"
            "• Trajet enregistré\n"
            "• Bouton d'urgence: 122"
        )
    
    def cancel_ride(self, instance):
        """Annuler la course (côté client)"""
        self.show_popup(
            "Annulation",
            "Voulez-vous vraiment annuler cette course ?\n\n"
            "⚠️ Des frais peuvent s'appliquer.",
            confirm=True
        )
    
    def go_home(self):
        """Retour à l'accueil"""
        self.tracking_enabled = False
        if self.manager and hasattr(self.manager, 'current'):
            self.manager.current = 'client_home'
    
    def show_popup(self, title, message, confirm=False):
        """Afficher un popup"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text=message, halign='center'))
        
        if confirm:
            btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
            btn_yes = Button(text='OUI', background_color=(0.8, 0.2, 0.2, 1))
            btn_no = Button(text='NON', background_color=(0.2, 0.6, 0.2, 1))
            
            popup = Popup(title=title, content=content, size_hint=(0.8, 0.5))
            
            def do_cancel(inst):
                popup.dismiss()
                self.process_cancellation()
            
            btn_yes.bind(on_press=do_cancel)
            btn_no.bind(on_press=popup.dismiss)
            
            btn_layout.add_widget(btn_yes)
            btn_layout.add_widget(btn_no)
            content.add_widget(btn_layout)
        else:
            btn_ok = Button(text='OK', size_hint_y=None, height=50)
            popup = Popup(title=title, content=content, size_hint=(0.7, 0.4))
            btn_ok.bind(on_press=popup.dismiss)
            content.add_widget(btn_ok)
        
        popup.open()
    
    def process_cancellation(self):
        """Traiter l'annulation (côté client)"""
        app = App.get_running_app()
        
        if hasattr(app, 'api_client') and self.course_code:
            result = app.api_client.cancel_course(self.course_code)
            if result.get('success'):
                print(f"✅ Course {self.course_code} annulée par le client")
                self.go_home()
            else:
                print(f"❌ Erreur annulation: {result.get('error')}")
    
    def on_enter(self):
        """Quand l'écran s'affiche"""
        self.tracking_enabled = True
        self.route_drawn = False
        self.current_phase = None
        self.map_already_opened = False
        self.annulation_popup_shown = False  # ⭐ Réinitialiser
        
        # Mettre à jour les infos initiales
        self.lbl_price.text = f'💰 [size=18][b]{self.price} KMF[/b][/size]'
        self.lbl_plate.text = f'[size=16]🚘 Plaque:[/size] [size=20][b][color=0088CC]{self.driver.get("plaque", "XX-000-XX")}[/color][/b][/size]'
        self.lbl_immatricule.text = f'🆔 [b]{self.driver.get("immatricule", "---")}[/b]'
        
        vehicule_complet = f"{self.driver.get('marque', '')} {self.driver.get('modele', '')}".strip()
        if self.driver.get('couleur'):
            vehicule_complet += f" ({self.driver.get('couleur')})"
        if vehicule_complet:
            self.lbl_vehicle.text = f'🚗 {vehicule_complet}'
        
        # Ouvrir automatiquement la carte
        if self.course_code:
            Clock.schedule_once(lambda dt: self.open_tracking_map_auto(), 1.5)
            print("🗺️ Ouverture automatique de la carte de suivi")

    def show_conducteur_refus_popup(self):
        """Popup spécifique quand le conducteur refuse la course"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        content.add_widget(Label(
            text="🔄 RECHERCHE D'UN AUTRE CONDUCTEUR",
            font_size='20sp',
            bold=True,
            color=(1, 0.5, 0, 1),
            size_hint_y=None,
            height=40
        ))
        
        content.add_widget(Label(
            text="Le conducteur a refusé la course.\n\n"
                 "Nous recherchons un autre conducteur\n"
                 "pour vous...",
            halign='center',
            font_size='16sp',
            size_hint_y=None,
            height=80
        ))
        
        popup = Popup(
            title='Recherche en cours',
            content=content,
            size_hint=(0.8, 0.45),
            auto_dismiss=False
        )
        
        popup.open()
        # Le popup se fermera automatiquement quand on change d'écran
        Clock.schedule_once(lambda dt: popup.dismiss(), 2.5)
    
    def return_to_search(self):
        """Retourner à l'écran de recherche"""
        self.tracking_enabled = False
        
        # Nettoyer les données de l'app
        app = App.get_running_app()
        if hasattr(app, 'current_course'):
            delattr(app, 'current_course')
        if hasattr(app, 'current_course_coords'):
            delattr(app, 'current_course_coords')
        
        # Retourner à l'écran d'attente (recherche)
        if self.manager and hasattr(self.manager, 'current'):
            if 'waiting_for_driver' in self.manager.screen_names:
                self.manager.current = 'waiting_for_driver'
            else:
                self.manager.current = 'client_home'
        print("🔄 Retour à la recherche de conducteur")
    
    def on_leave(self):
        """Nettoyer quand on quitte le suivi"""
        self.tracking_enabled = False
        self.route_drawn = False
        self.map_already_opened = False
        self.annulation_popup_shown = False
        
        # Arrêter les mises à jour
        Clock.unschedule(self.update_tracking)
        
        # ⭐ Nettoyer les données de l'app
        app = App.get_running_app()
        if hasattr(app, 'current_course'):
            delattr(app, 'current_course')
        if hasattr(app, 'current_course_coords'):
            delattr(app, 'current_course_coords')
        
        print("👋 Suivi arrêté et nettoyé")