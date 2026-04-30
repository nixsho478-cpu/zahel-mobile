# navigation_mapbox.py - Écran de navigation conducteur (VERSION AVEC APPEL ET ANNULATION CLIENT)
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.app import App

try:
    from plyer import gps
    GPS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    GPS_AVAILABLE = False


# ⭐⭐⭐ CLASSES DE POPUP DÉDIÉES ⭐⭐⭐
class ConfirmFinishPopup(Popup):
    """Popup de confirmation de fin de course"""
    
    def __init__(self, callback, **kwargs):
        super(ConfirmFinishPopup, self).__init__(**kwargs)
        self.callback = callback
        self.title = '🏁 Confirmation'
        self.size_hint = (0.8, 0.45)
        self.auto_dismiss = False
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(
            text="[size=18]Terminer la course ?[/size]\n\n"
                 "• Le client sera facturé\n"
                 "• Vos statistiques seront mises à jour",
            markup=True,
            halign='center'
        ))
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_yes = Button(text='✅ OUI, TERMINER', background_color=(0.2, 0.6, 0.2, 1))
        btn_yes.bind(on_press=self.on_yes)
        btn_no = Button(text='❌ NON, ANNULER', background_color=(0.8, 0.2, 0.2, 1))
        btn_no.bind(on_press=self.on_no)
        
        btn_layout.add_widget(btn_yes)
        btn_layout.add_widget(btn_no)
        content.add_widget(btn_layout)
        
        self.content = content
    
    def on_yes(self, instance):
        self.dismiss()
        if self.callback:
            self.callback()
    
    def on_no(self, instance):
        self.dismiss()


class WarningPopup(Popup):
    """Popup d'avertissement"""
    
    def __init__(self, title, message, **kwargs):
        super(WarningPopup, self).__init__(**kwargs)
        self.title = title
        self.size_hint = (0.8, 0.4)
        self.auto_dismiss = False
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text=message, halign='center'))
        
        btn = Button(text='OK', size_hint_y=None, height=50, background_color=(0.2, 0.5, 0.8, 1))
        btn.bind(on_press=self.dismiss)
        
        content.add_widget(btn)
        self.content = content


class CancelConfirmPopup(Popup):
    """Popup de confirmation d'annulation de course"""
    
    def __init__(self, callback, **kwargs):
        super(CancelConfirmPopup, self).__init__(**kwargs)
        self.callback = callback
        self.title = '⚠️ Annuler la course ?'
        self.size_hint = (0.8, 0.45)
        self.auto_dismiss = False
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(
            text="[size=18]⚠️ Annuler la course ?[/size]\n\n"
                 "• Le client sera notifié\n"
                 "• Cette action est irréversible\n"
                 "• Des pénalités peuvent s'appliquer",
            markup=True,
            halign='center'
        ))
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_no = Button(text='❌ NON, CONTINUER', background_color=(0.2, 0.6, 0.2, 1))
        btn_no.bind(on_press=self.on_no)
        btn_yes = Button(text='✅ OUI, ANNULER', background_color=(0.8, 0.2, 0.2, 1))
        btn_yes.bind(on_press=self.on_yes)
        
        btn_layout.add_widget(btn_no)
        btn_layout.add_widget(btn_yes)
        content.add_widget(btn_layout)
        
        self.content = content
    
    def on_yes(self, instance):
        self.dismiss()
        if self.callback:
            self.callback()
    
    def on_no(self, instance):
        self.dismiss()


class SuccessPopup(Popup):
    """Popup de succès"""
    
    def __init__(self, title, message, **kwargs):
        super(SuccessPopup, self).__init__(**kwargs)
        self.title = title
        self.size_hint = (0.7, 0.3)
        self.auto_dismiss = True
        
        content = BoxLayout(orientation='vertical', padding=20)
        content.add_widget(Label(text=message, halign='center'))
        self.content = content


# ⭐⭐⭐ ÉCRAN DE NAVIGATION ⭐⭐⭐
class NavigationScreenMapbox(Screen):
    
    def __init__(self, **kwargs):
        super(NavigationScreenMapbox, self).__init__(**kwargs)

        app = App.get_running_app()
        self.api_client = getattr(app, 'api_client', None)
        
        self.course_code = None
        self.is_navigating = False
        self.current_phase = 0  # 0=prêt, 1=vers client, 2=vers destination
        
        self.driver_pos = (-11.6980, 43.2560)
        self.client_pos = (-11.7040, 43.2610)
        self.dest_pos = (-11.7100, 43.2650)
        
        # ⭐ Stocker le téléphone du client (proxy de préférence)
        self.client_phone = None
        
        self.gps_available = GPS_AVAILABLE
        self.gps_location = None
        self.use_real_gps = True  # Mettre à False pour tester sans GPS
        
        self.build_interface()
        print("🗺️ NavigationScreenMapbox initialisée")
    
    def build_interface(self):
        main_layout = BoxLayout(orientation='vertical', spacing=5, padding=[10, 5, 10, 5])
        
        header = BoxLayout(size_hint=(1, 0.06))
        header.add_widget(Label(text='[b]🚗 ZAHEL - Navigation[/b]', markup=True, font_size='16sp', halign='center'))
        
        self.btn_view_map = Button(
            text='[size=18]🗺️ OUVRIR LA CARTE[/size]',
            markup=True,
            size_hint=(1, 0.10),
            background_color=(0.2, 0.6, 0.4, 1),
            bold=True
        )
        self.btn_view_map.bind(on_press=self.open_navigation_map)
        
        self.status_label = Label(
            text='[size=16][color=FF9900]📍 Prêt à démarrer[/color][/size]',
            markup=True,
            halign='center',
            size_hint=(1, 0.06)
        )
        
        info_box = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=5, padding=[10, 5])
        self.distance_label = Label(text='📏 Distance: -- km', font_size='16sp', halign='left')
        self.time_label = Label(text='⏱️ Temps estimé: -- min', font_size='14sp', halign='left')
        self.gps_label = Label(text='📍 GPS: Simulation', font_size='12sp', color=(0.5, 0.5, 0.5, 1), halign='left')
        info_box.add_widget(self.distance_label)
        info_box.add_widget(self.time_label)
        info_box.add_widget(self.gps_label)
        
        self.progress_bar = ProgressBar(max=100, value=0, size_hint=(1, 0.05))
        
        self.instruction_label = Label(
            text='Appuyez sur DÉMARRER pour commencer',
            font_size='14sp',
            color=(0.2, 0.4, 0.8, 1),
            size_hint=(1, 0.08),
            halign='center'
        )
        
        # ⭐⭐⭐ SECTION ACTIONS AVEC BOUTON APPELER ⭐⭐⭐
        self.actions_section = BoxLayout(size_hint=(1, 0.12), spacing=8, padding=[10, 5])
        
        # Bouton principal (Démarrer / Vers destination / Terminer)
        self.btn_primary = Button(
            text='▶ DÉMARRER',
            background_color=(0, 0.6, 0.2, 1),
            bold=True,
            size_hint=(0.35, 1)
        )
        self.btn_primary.bind(on_press=self.primary_action)
        
        # Bouton Centrer
        btn_center = Button(
            text='📍',
            background_color=(0.4, 0.4, 0.4, 1),
            bold=True,
            size_hint=(0.12, 1),
            font_size='18sp'
        )
        btn_center.bind(on_press=self.center_map)
        
        # ⭐⭐⭐ NOUVEAU BOUTON APPELER ⭐⭐⭐
        self.btn_call = Button(
            text='📞',
            background_color=(0.2, 0.6, 0.2, 1),
            bold=True,
            size_hint=(0.12, 1),
            font_size='18sp'
        )
        self.btn_call.bind(on_press=self.call_client)
        
        # Bouton secondaire (Annuler)
        self.btn_secondary = Button(
            text='❌',
            background_color=(0.8, 0.2, 0.2, 1),
            bold=True,
            size_hint=(0.12, 1),
            font_size='18sp'
        )
        self.btn_secondary.bind(on_press=self.secondary_action)
        
        # Ajouter tous les boutons
        self.actions_section.add_widget(self.btn_primary)
        self.actions_section.add_widget(btn_center)
        self.actions_section.add_widget(self.btn_call)
        self.actions_section.add_widget(self.btn_secondary)
        
        main_layout.add_widget(header)
        main_layout.add_widget(self.btn_view_map)
        main_layout.add_widget(self.status_label)
        main_layout.add_widget(info_box)
        main_layout.add_widget(self.progress_bar)
        main_layout.add_widget(self.instruction_label)
        main_layout.add_widget(self.actions_section)
        main_layout.add_widget(Label(size_hint=(1, 0.15)))
        
        self.add_widget(main_layout)
    
    # ⭐⭐⭐ NOUVELLE MÉTHODE : APPELER LE CLIENT ⭐⭐⭐
    def call_client(self, instance):
        """Appeler le client (via numéro proxy ou direct)"""
        print("📞 Tentative d'appel du client...")
        print(f"   client_phone = {self.client_phone}")
    
        if self.client_phone:
            import webbrowser
            webbrowser.open(f"tel:{self.client_phone}")
            print(f"📞 Appel du client: {self.client_phone[:4]}...")
        
            popup = SuccessPopup(
                title="📞 Appel en cours",
                message=f"Appel du client en cours..."
            )
            popup.open()
        else:
            # ⭐ Message plus informatif
            popup = WarningPopup(
                title="📞 Information",
                message="Le numéro du client n'est pas disponible.\n\n"
                        "Le client sera notifié de votre arrivée.\n"
                        "Utilisez le klaxon ou attendez sur place."
            )
            popup.open()
    
    def primary_action(self, instance):
        """Action principale (Démarrer / Vers destination / Terminer)"""
        if self.current_phase == 0:
            self.start_navigation()
        elif self.current_phase == 1:
            self.start_to_destination()
        elif self.current_phase == 2:
            popup = ConfirmFinishPopup(callback=self.process_finish_course)
            popup.open()
    
    def secondary_action(self, instance):
        """Action secondaire (Annuler)"""
        if self.current_phase == 0:
            # Phase 0 : Refuser la course (avant de démarrer)
            self.refuse_course()
        elif self.current_phase == 1:
            # Phase 1 : en route vers client - annuler avec pénalité
            popup = CancelConfirmPopup(callback=self.process_cancellation)
            popup.open()
        elif self.current_phase == 2:
            # Phase 2 : en course - ne peut pas annuler
            popup = WarningPopup(
                title="⛔ Action impossible",
                message="Vous êtes en pleine course !\n\n"
                        "Utilisez le bouton 'TERMINER'\n"
                        "pour terminer la course normalement."
            )
            popup.open()


    def refuse_course(self):
        """Refuser la course (avant de démarrer)"""
        print("❌ Refus de la course par le conducteur...")
        
        # Récupérer le token depuis l'application
        app = App.get_running_app()
        token = None
        
        # Essayer plusieurs sources pour le token
        if hasattr(self, 'api_client') and self.api_client and hasattr(self.api_client, 'token'):
            token = self.api_client.token
            print(f"✅ Token depuis self.api_client: {token[:10]}...")
        elif hasattr(app, 'api_client') and app.api_client and hasattr(app.api_client, 'token'):
            token = app.api_client.token
            print(f"✅ Token depuis app.api_client: {token[:10]}...")
        elif hasattr(app, 'immatricule'):
            token = app.immatricule
            print(f"✅ Token depuis app.immatricule: {token[:10]}...")
        elif hasattr(app, 'conducteur_data') and app.conducteur_data:
            token = app.conducteur_data.get('token')
            print(f"✅ Token depuis app.conducteur_data: {token[:10] if token else 'None'}...")
        
        if not token:
            print("❌ Aucun token disponible - Impossible d'annuler via l'API")
            # Même sans token, on retourne au dashboard
            self.is_navigating = False
            Clock.unschedule(self.send_gps_position_to_api)
            Clock.unschedule(self.check_course_cancelled)
            self.stop_gps()
            
            popup = SuccessPopup(
                title="✅ Course refusée",
                message="Retour au dashboard..."
            )
            popup.open()
            Clock.schedule_once(lambda dt: self.return_to_dashboard(), 2)
            return
        
        # Appeler l'API pour annuler
        if self.course_code:
            try:
                import requests
                from config.config import Config
                
                API_BASE_URL = Config.get_api_url()
                
                print(f"📡 Appel API annulation: {API_BASE_URL}/api/courses/{self.course_code}/annuler")
                print(f"   Token: {token[:10]}...")
                
                response = requests.post(
                    f"{API_BASE_URL}/api/courses/{self.course_code}/annuler",
                    headers={"Authorization": token, "Content-Type": "application/json"},
                    json={"raison": "conducteur_refuse"},
                    timeout=10
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"✅ Course {self.course_code} refusée - Le client va rechercher un autre conducteur")
                    else:
                        print(f"⚠️ Erreur API: {result.get('error')}")
                else:
                    print(f"⚠️ HTTP {response.status_code}: {response.text[:100]}")
            except Exception as e:
                print(f"❌ Exception refus course: {e}")
                import traceback
                traceback.print_exc()
        
        # Arrêter la navigation
        self.is_navigating = False
        Clock.unschedule(self.send_gps_position_to_api)
        Clock.unschedule(self.check_course_cancelled)
        self.stop_gps()
        
        # Message
        popup = SuccessPopup(
            title="✅ Course refusée",
            message="La course a été refusée.\n"
                    "Le client va rechercher un autre conducteur.\n"
                    "Retour au dashboard..."
        )
        popup.open()
        
        # Retour au dashboard après délai
        Clock.schedule_once(lambda dt: self.return_to_dashboard(), 2)

    
    def process_cancellation(self):
        """Traiter l'annulation de la course et notifier le client"""
        print("❌ Annulation de la course par le conducteur...")
        
        # 1. Appeler l'API pour annuler la course avec motif
        if hasattr(self, 'api_client') and self.api_client and self.course_code:
            try:
                # ⭐ Envoyer le motif "conducteur"
                import requests
                from config.config import Config
                
                API_BASE_URL = Config.get_api_url()
                token = self.api_client.token
                
                response = requests.post(
                    f"{API_BASE_URL}/api/courses/{self.course_code}/annuler",
                    headers={"Authorization": token, "Content-Type": "application/json"},
                    json={"raison": "annulation_conducteur"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"✅ Course {self.course_code} annulée via API")
                        print(f"   Actions: {result.get('actions_appliquees', [])}")
                    else:
                        print(f"⚠️ Erreur API annulation: {result.get('error')}")
                else:
                    print(f"⚠️ HTTP {response.status_code}: {response.text[:100]}")
            except Exception as e:
                print(f"❌ Exception annulation API: {e}")
        
        # 2. Arrêter la navigation
        self.is_navigating = False
        Clock.unschedule(self.send_gps_position_to_api)
        Clock.unschedule(self.check_course_cancelled)  # ⭐ AJOUTER
        self.stop_gps()
        
        # 3. Message de confirmation
        popup = SuccessPopup(
            title="✅ Course annulée",
            message="La course a été annulée.\n"
                    "Le client est notifié.\n"
                    "Retour au dashboard..."
        )
        popup.open()
        
        # 4. Retour au dashboard après délai
        Clock.schedule_once(lambda dt: self.return_to_dashboard(), 2)
        print("👋 Retour au dashboard après annulation")
    
    def start_navigation(self):
        """Démarrer la navigation vers le client"""
        self.status_label.text = '[size=16][color=FF9900]🚗 En route vers le client[/color][/size]'
        self.instruction_label.text = 'Direction : point de prise en charge'
        self.current_phase = 1
        self.btn_primary.text = '▶ VERS DESTINATION'
        self.btn_primary.background_color = (0, 0.8, 0, 1)
        self.btn_secondary.text = '❌'
        self.btn_secondary.disabled = False
        self.progress_bar.value = 30
        self.is_navigating = True
        
        # Activer le bouton d'appel
        self.btn_call.disabled = False
        
        # Démarrer le GPS
        self.start_gps()
        
        # Envoyer la position toutes les 3 secondes
        Clock.schedule_interval(self.send_gps_position_to_api, 3)
        print("✅ Navigation démarrée - Phase 1")
    
    def start_to_destination(self):
        """Démarrer vers la destination - AVEC APPEL API"""
        print("🔄 Passage en Phase 2 - Appel API /commencer")
    
        # ⭐⭐⭐ RÉCUPÉRER L'API CLIENT CORRECTEMENT ⭐⭐⭐
        app = App.get_running_app()
    
        # Essayer plusieurs sources possibles
        api_client = None
    
        # 1. Depuis self.api_client
        if hasattr(self, 'api_client') and self.api_client:
            api_client = self.api_client
            print("✅ API client trouvé dans self.api_client")
    
        # 2. Depuis l'application
        elif hasattr(app, 'api_client') and app.api_client:
            api_client = app.api_client
            print("✅ API client trouvé dans app.api_client")
            self.api_client = api_client
    
        # 3. Depuis app.conducteur_api_client
        elif hasattr(app, 'conducteur_api_client') and app.conducteur_api_client:
            api_client = app.conducteur_api_client
            print("✅ API client trouvé dans app.conducteur_api_client")
            self.api_client = api_client
    
        # 4. Vérifier si on a un token conducteur
        if not api_client:
            print("❌ Aucun API client trouvé !")
            print("   Tentative de création d'un nouveau client...")
        
            try:
                from api.client import APIClient
                api_client = APIClient()
            
                if hasattr(app, 'conducteur_token'):
                    token = app.conducteur_token
                    api_client.set_token(token, 'conducteur')
                    print(f"✅ Nouvel API client créé avec token: {token[:10]}...")
                    self.api_client = api_client
                elif hasattr(app, 'immatricule'):
                    token = app.immatricule
                    api_client.set_token(token, 'conducteur')
                    print(f"✅ Nouvel API client créé avec token: {token[:10]}...")
                    self.api_client = api_client
                else:
                    print("❌ Impossible de trouver un token conducteur")
            except Exception as e:
                print(f"❌ Erreur création API client: {e}")
    
        # ⭐⭐⭐ APPELER L'API POUR CHANGER LE STATUT ⭐⭐⭐
        if api_client and self.course_code:
            try:
                print(f"📡 Appel API /commencer pour course: {self.course_code}")
                result = api_client.start_course(self.course_code)
            
                if result.get('success'):
                    print(f"✅ API: Course {self.course_code} commencée (statut: en_cours)")
                else:
                    print(f"⚠️ API: Erreur /commencer - {result.get('error')}")
            except Exception as e:
                print(f"❌ Exception appel API /commencer: {e}")
        else:
            if not api_client:
                print("⚠️ Pas d'API client disponible")
            if not self.course_code:
                print("⚠️ Pas de code course disponible")
    
        # Mise à jour de l'interface
        self.status_label.text = '[size=16][color=FF9900]🛣️ En route vers la destination[/color][/size]'
        self.instruction_label.text = 'Direction : destination finale'
        self.current_phase = 2
        self.btn_primary.text = '🏁 TERMINER'
        self.btn_primary.background_color = (0.8, 0.4, 0.0, 1)
        self.btn_secondary.text = '❌'
        self.btn_secondary.disabled = True  # Désactivé en phase 2
        self.progress_bar.value = 60
    
        # Ouvrir la carte avec les nouvelles coordonnées
        import webbrowser
        url = (f"http://localhost:8080?"
               f"depart_lat={self.client_pos[0]}&depart_lng={self.client_pos[1]}"
               f"&arrivee_lat={self.dest_pos[0]}&arrivee_lng={self.dest_pos[1]}")
        webbrowser.open_new(url)
        print(f"✅ Navigation démarrée - Phase 2")
        print(f"   URL: {url}")
    
    def process_finish_course(self):
        """Traiter la fin de course"""
        if hasattr(self, 'api_client') and self.api_client and self.course_code:
            result = self.api_client.finish_course(self.course_code)
            
            if result.get('success'):
                print(f"✅ Course {self.course_code} terminée - Statistiques mises à jour")
                Clock.unschedule(self.send_gps_position_to_api)
                self.stop_gps()
                self.is_navigating = False
                
                popup = SuccessPopup(
                    title="✅ Course terminée !",
                    message="Statistiques mises à jour.\nRetour au dashboard..."
                )
                popup.open()
                
                Clock.schedule_once(lambda dt: self.return_to_dashboard(), 2)
            else:
                popup = WarningPopup(
                    title="❌ Erreur",
                    message=f"Impossible de terminer:\n{result.get('error', 'Erreur inconnue')}"
                )
                popup.open()
        else:
            popup = WarningPopup(
                title="❌ Erreur",
                message="API client non disponible"
            )
            popup.open()
    
    def force_exit(self):
        """Forcer la sortie (seulement en phase 0)"""
        Clock.unschedule(self.send_gps_position_to_api)
        self.stop_gps()
        self.manager.current = 'dashboard'
        print("👋 Sortie de navigation")
    
    def return_to_dashboard(self):
        """Retour au dashboard"""
        self.manager.current = 'dashboard'
    
    def open_navigation_map(self, instance):
        """Ouvrir la carte de navigation"""
        import webbrowser
        if self.current_phase == 0:
            url = f"http://localhost:8080?depart_lat={self.driver_pos[0]}&depart_lng={self.driver_pos[1]}&arrivee_lat={self.client_pos[0]}&arrivee_lng={self.client_pos[1]}"
        elif self.current_phase == 1:
            url = f"http://localhost:8080?depart_lat={self.driver_pos[0]}&depart_lng={self.driver_pos[1]}&arrivee_lat={self.client_pos[0]}&arrivee_lng={self.client_pos[1]}"
        else:
            url = f"http://localhost:8080?depart_lat={self.client_pos[0]}&depart_lng={self.client_pos[1]}&arrivee_lat={self.dest_pos[0]}&arrivee_lng={self.dest_pos[1]}"
        webbrowser.open_new(url)
        print(f"🌐 Carte ouverte: {url}")
    
    def center_map(self, instance):
        """Recentrer la carte (placeholder)"""
        print("📍 Centrer la carte")
    
    # ⭐⭐⭐ MÉTHODES GPS ⭐⭐⭐
    def start_gps(self):
        """Démarrer le GPS"""
        if self.gps_available and self.use_real_gps:
            try:
                gps.configure(on_location=self.on_gps_location, on_status=self.on_gps_status)
                gps.start(minTime=2000, minDistance=5)
                self.gps_label.text = '📍 GPS: Démarré'
                print("✅ GPS démarré")
            except Exception as e:
                print(f"❌ Erreur démarrage GPS: {e}")
                self.gps_available = False
                self.gps_label.text = '📍 GPS: Simulation'
        else:
            self.gps_label.text = '📍 GPS: Simulation'
            print("ℹ️ Mode simulation GPS")
    
    def on_gps_location(self, **kwargs):
        """Callback appelé quand le GPS a une nouvelle position"""
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        accuracy = kwargs.get('accuracy', 0)
        
        if lat and lon:
            self.gps_location = (lat, lon)
            self.driver_pos = (lat, lon)
            self.gps_label.text = f'📍 GPS: {lat:.6f}, {lon:.6f} (±{accuracy:.0f}m)'
    
    def on_gps_status(self, **kwargs):
        """Callback pour le statut GPS"""
        status = kwargs.get('status', 'unknown')
        if status == 'provider-enabled':
            self.gps_label.text = '📍 GPS: Actif'
        elif status == 'provider-disabled':
            self.gps_label.text = '⚠️ GPS: Désactivé - Activez la localisation'
        else:
            self.gps_label.text = f'📍 GPS: {status}'
    
    def stop_gps(self):
        """Arrêter le GPS"""
        if self.gps_available and self.use_real_gps:
            try:
                gps.stop()
                print("✅ GPS arrêté")
            except:
                pass
    
    def send_gps_position_to_api(self, dt=None):
        """Envoyer la position GPS à l'API"""
        if not self.is_navigating:
            return
        
        if self.gps_available and self.use_real_gps and self.gps_location:
            lat, lon = self.gps_location
            source = "GPS"
        else:
            lat, lon = self.driver_pos
            source = "SIMULATION"
        
        if hasattr(self, 'api_client') and self.api_client:
            try:
                result = self.api_client.update_driver_position(lat, lon)
                if result.get('success'):
                    print(f"📍 Position {source} envoyée: ({lat:.6f}, {lon:.6f})")
            except Exception as e:
                print(f"⚠️ Erreur envoi position: {e}")
    
    def on_enter(self):
        """Quand on arrive sur l'écran"""
        app = App.get_running_app()
        self.course_code = getattr(app, 'current_course', None)
        
        course_coords = getattr(app, 'current_course_coords', None)
        if course_coords:
            self.client_pos = course_coords.get('depart', self.client_pos)
            self.dest_pos = course_coords.get('arrivee', self.dest_pos)
            
            # ⭐ Récupérer le téléphone du client (proxy)
            self.client_phone = course_coords.get('client_phone', 
                                                   course_coords.get('client_telephone', None))
            
            distance = self.calculate_distance(self.driver_pos, self.client_pos) + self.calculate_distance(self.client_pos, self.dest_pos)
            self.distance_label.text = f'📏 Distance totale: {distance:.1f} km'
            self.time_label.text = f'⏱️ Temps estimé: {int(distance * 4)} min'
        
        # Réinitialiser l'interface
        self.current_phase = 0
        self.btn_primary.text = '▶ DÉMARRER'
        self.btn_primary.background_color = (0, 0.6, 0.2, 1)
        self.btn_secondary.text = '❌'
        self.btn_secondary.disabled = False
        self.btn_call.disabled = False
        self.progress_bar.value = 0
        self.status_label.text = '[size=16][color=FF9900]📍 Prêt à démarrer[/color][/size]'
        
        # Démarrer le GPS
        self.start_gps()
        
        # Ouvrir la carte automatiquement
        Clock.schedule_once(lambda dt: self.open_navigation_map(None), 1.5)
        print(f"🗺️ NavigationScreenMapbox activé - Course: {self.course_code}")

        # ⭐⭐⭐ VÉRIFIER LE STATUT TOUTES LES 5 SECONDES ⭐⭐⭐
        Clock.schedule_interval(self.check_course_cancelled, 5)
        print("🔍 Vérification statut course activée (toutes les 5s)")
    
    def check_course_cancelled(self, dt):
        """Vérifier si la course a été annulée par le client"""
        if not self.course_code:
            return
        
        # Ne vérifier que si en navigation active
        if not self.is_navigating and self.current_phase == 0:
            return
        
        try:
            import requests
            from config.config import Config
            
            API_BASE_URL = Config.get_api_url()
            response = requests.get(
                f"{API_BASE_URL}/api/courses/{self.course_code}/statut",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                course = data.get('course', {})
                statut = course.get('statut', '')
                
                if statut == 'annulee':
                    print("⚠️ COURSE ANNULÉE PAR LE CLIENT !")
                    Clock.unschedule(self.check_course_cancelled)
                    Clock.unschedule(self.send_gps_position_to_api)
                    self.stop_gps()
                    self.is_navigating = False
                    
                    popup = WarningPopup(
                        title="❌ Course annulée",
                        message="Le client a annulé la course.\n\n"
                                "Retour au dashboard..."
                    )
                    popup.open()
                    
                    Clock.schedule_once(lambda dt: self.return_to_dashboard(), 2)
        except Exception as e:
            pass  # Ignorer les erreurs silencieusement

    def calculate_distance(self, pos1, pos2):
        """Calculer la distance entre deux points en km"""
        from math import radians, sin, cos, sqrt, atan2
        lat1, lon1 = pos1
        lat2, lon2 = pos2
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return round(R * c, 1)
    
    def on_leave(self):
        """Nettoyer quand on quitte l'écran"""
        Clock.unschedule(self.send_gps_position_to_api)
        Clock.unschedule(self.check_course_cancelled)  # ⭐ AJOUTER
        self.stop_gps()
        print("👋 NavigationScreenMapbox quitté")