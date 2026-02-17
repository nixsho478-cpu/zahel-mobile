# ✅ AJOUTE CES 3 LIGNES TOUT AU DÉBUT
import os
import sys
os.environ['KIVY_NO_ARGS'] = '1'  # ✅ IMPORTANT : Désactive Kivy arguments

# main.py – CORRECTION COMPLÈTE

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch  # ← Pour les paramètres
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy_garden.mapview import MapView, MapMarker  # <-- COMMENTE
from kivy.clock import Clock
from datetime import datetime
from urllib.parse import quote
import json
import threading
import time
import os
import requests
import random
import sys
import webbrowser
import math

# Filtrer l'argument --driver avant que Kivy ne démarre
IS_DRIVER_MODE = False
if '--driver' in sys.argv:
    IS_DRIVER_MODE = True
    sys.argv.remove('--driver')  # Retirer pour que Kivy ne se plaigne pas
    print(f"🚗 ARGUMENT --driver DÉTECTÉ")
elif '--conducteur' in sys.argv:
    IS_DRIVER_MODE = True
    sys.argv.remove('--conducteur')
    print(f"🚗 ARGUMENT --conducteur DÉTECTÉ")
elif '--chauffeur' in sys.argv:
    IS_DRIVER_MODE = True
    sys.argv.remove('--chauffeur')
    print(f"🚗 ARGUMENT --chauffeur DÉTECTÉ")

print(f"🚗 MODE APPLICATION: {'CONDUCTEUR' if IS_DRIVER_MODE else 'CLIENT'}")

# Import du client API
try:
    from api.client import APIClient

    # ✅ CRÉER UNE INSTANCE UNIQUE
    _api_client = APIClient()
    
    # ✅ FONCTION POUR RÉCUPÉRER L'INSTANCE
    def get_api_client():
        global _api_client
        return _api_client
    
    # ✅ VARIABLE GLOBALE (pour compatibilité)
    api_client = _api_client
    
    API_MODULE_EXISTS = True
    print("✅ API Client importé")

    # Tester la connexion (si la méthode existe)
    if hasattr(api_client, "test_connection"):
        if api_client.test_connection():
            print("✅ Connexion API réussie")
        else:
            print("⚠️  Impossible de se connecter à l'API")
    else:
        print("⚠️  Méthode test_connection non disponible")
except ImportError as e:
    API_MODULE_EXISTS = False
    api_client = None
    print(f"⚠️  Impossible d'importer api.client: {e}")

# Configuration fenêtre
Window.size = (360, 640)
Window.title = "ZAHEL – Conducteur"

# ==================== CLIENT API SIMULÉ ====================


class APIClientSimule:
    """Client API simulé si le vrai n'existe pas"""

    def __init__(self):
        self.token = None
        self.base_url = "http://localhost:5001"

    def login(self, immatricule, password):
        """Simule une connexion"""
        print(f"🔐 Connexion simulée: {immatricule}")
        self.token = immatricule
        return {"success": True, "token": immatricule}

    def get_conducteur_info(self):
        """Simule les infos conducteur"""
        return {
            "success": True,
            "conducteur": {
                "immatricule": "ZH-327KYM",
                "nom": "Ahmed Test",
                "performance": {
                    "courses_effectuees": 1,
                    "gains_totaux": 1200.0,
                    "note_moyenne": 5.0,
                },
            },
        }

    def get_available_courses(self):
        """Simule les courses disponibles"""
        # Simulation: retourne une course vide pour tester
        return {"success": True, "count": 0, "courses": []}

    def accept_course(self, course_code):
        """Simule l'acceptation d'une course"""
        print(f"✅ Course acceptée (simulation): {course_code}")
        return {"success": True, "message": "Course acceptée"}

    def toggle_status(self, disponible):
        """Simule le changement de statut"""
        return {"success": True}


# ==================== NOUVEAUX ÉCRANS CLIENT ====================


class ClientLoginScreen(Screen):
    """Écran de connexion client"""

    def __init__(self, **kwargs):
        super(ClientLoginScreen, self).__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=50, spacing=30)

        # Titre
        title = Label(
            text="[b]Connexion Client ZAHEL[/b]",
            markup=True,
            font_size="24sp",
            halign="center",
        )

        # Téléphone
        self.txt_phone = TextInput(
            hint_text="Numéro de téléphone (ex: +26934011111)",
            multiline=False,
            size_hint=(1, None),
            height=50,
            font_size="16sp",
        )

        # Mot de passe
        self.txt_password = TextInput(
            hint_text="Mot de passe",
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=50,
            font_size="16sp",
        )

        # Bouton connexion
        btn_login = Button(
            text="[size=18][b]SE CONNECTER[/b][/size]",
            markup=True,
            size_hint=(1, None),
            height=60,
            background_color=(0.2, 0.5, 0.8, 1),
        )
        btn_login.bind(on_press=self.login)

        # Bouton inscription
        btn_register = Button(
            text="Créer un compte",
            size_hint=(0.6, None),
            height=50,
            pos_hint={"center_x": 0.5},
        )
        btn_register.bind(on_press=self.go_to_register)

        # Bouton retour
        btn_back = Button(
            text="← Retour",
            size_hint=(0.4, None),
            height=40,
            pos_hint={"center_x": 0.5},
        )
        btn_back.bind(on_press=self.go_back)

        layout.add_widget(title)
        layout.add_widget(self.txt_phone)
        layout.add_widget(self.txt_password)
        layout.add_widget(btn_login)
        layout.add_widget(btn_register)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def login(self, instance):
        # ✅ AJOUTE AU DÉBUT
        global api_client, API_MODULE_EXISTS

        # ✅ 1. SUPPRIMER TOUTE ANCIENNE SESSION
        try:
            if os.path.exists('session.json'):
                os.remove('session.json')
                print("🗑️ Ancienne session supprimée")
        except Exception as e:
            print(f"⚠️ Erreur suppression session: {e}")
    
        phone = self.txt_phone.text.strip()
        password = self.txt_password.text.strip()

        """Connexion avec l'API réelle"""
        phone = self.txt_phone.text.strip()
        password = self.txt_password.text.strip()

        if not phone or not password:
            self.show_popup("Erreur", "Veuillez remplir tous les champs")
            return

        print(f"Tentative de connexion: {phone}")
    
        # ✅ AFFICHER L'ÉTAT AVANT CONNEXION
        print("\n🔍 ÉTAT AVANT CONNEXION:")
        print(f"   api_client.token avant: {getattr(api_client, 'token', 'None')}")
        print(f"   api_client.user_type avant: {getattr(api_client, 'user_type', 'None')}")

        # Désactiver le bouton
        instance.disabled = True
        instance.text = "Connexion en cours..."

        # Utiliser l'API réelle si disponible
        if api_client and API_MODULE_EXISTS:
            # Lancer dans un thread pour ne pas bloquer l'interface
            import threading

            def do_login():
                result = api_client.client_login(phone, password)
                from kivy.clock import Clock
            
                def process_result(dt):
                    print("\n🔍 RÉSULTAT API REÇU:")
                    print(f"   Résultat complet: {result}")
                    self.handle_login_result(result, instance)
                
                    # ✅ APPELER LE DEBUG APRÈS TRAITEMENT
                    self.debug_api_client_state()
            
                Clock.schedule_once(process_result, 0)

            threading.Thread(target=do_login, daemon=True).start()
        else:
            # Simulation
            print("⚠️  Utilisation de la simulation (API non disponible)")
            from kivy.clock import Clock
        
            def simulate(dt):
                result = {
                    'success': True, 
                    'token': 'simulated_token_' + phone,
                    'client': {'telephone': phone}
                }
                self.handle_login_result(result, instance)
                self.debug_api_client_state()
        
            Clock.schedule_once(simulate, 1)
        # APRÈS la connexion réussie
        print(f"\n{'='*60}")
        print(f"🎯 APRÈS CONNEXION - DEBUG")
        print(f"🎯 Redirection vers: client_home")
        print(f"🎯 Écran actuel avant: {self.manager.current}")
    
        # Rediriger VERS client_home
        self.manager.current = 'client_home'
    
        print(f"🎯 Écran actuel après: {self.manager.current}")
        print(f"{'='*60}\n")

    def go_back(self, instance):
        """Retour à la sélection"""
        self.manager.current = "selection"

    def handle_login_result(self, result, instance):
        """Gérer le résultat de la connexion"""
        global api_client, API_MODULE_EXISTS
    
        # Réactiver le bouton
        instance.disabled = False
        instance.text = "Se connecter"
    
        print(f"🔍 Résultat connexion reçu: {result}")
    
        if result.get('success'):
            print("✅ Connexion API réussie!")
        
            # ✅ EXTRAIRE LE TOKEN CORRECTEMENT
            token = result.get('token')
            if not token:
                # Essayer un autre format de réponse
                data = result.get('data', {})
                token = data.get('token')
        
            print(f"✅ Token reçu: {token}")
        
            if token:
                # ✅ ÉTAPE CRITIQUE : CONFIGURER LE TOKEN DANS API_CLIENT
                if api_client and API_MODULE_EXISTS:
                    success = api_client.set_token(token, 'client')
                    if success:
                        print(f"✅ Token configuré dans api_client")
                        print(f"   Token: {token}")
                        print(f"   User type: client")
                    else:
                        print(f"❌ Erreur configuration api_client")
            
                # Stocker dans l'application
                from kivy.app import App
                app = App.get_running_app()
            
                # Créer client_data
                client_info = result.get('client', {})
                if not client_info:
                    client_info = result.get('data', {}).get('client', {})
            
                app.client_data = {
                    'token': token,
                    'telephone': self.txt_phone.text.strip(),
                    'user_type': 'client',
                    **client_info  # Ajouter d'autres infos client
                }
            
                # ✅ AUSSI STOCKER LE TÉLÉPHONE DANS L'APP
                app.telephone = self.txt_phone.text.strip()
            
                print(f"✅ Client data stocké: {app.client_data}")
            
                # ✅ SAUVEGARDER LA SESSION
                self.save_session('client', self.txt_phone.text.strip(), token)
            
                # Aller à l'accueil client
                self.manager.current = 'client_home'
            
            else:
                print("❌ Aucun token dans la réponse")
                self.show_popup("Erreur", "Token manquant dans la réponse")
            
        else:
            error = result.get('error', 'Erreur inconnue')
            print(f"❌ Erreur connexion: {error}")
            self.show_popup("Erreur", f"Connexion échouée: {error}")

    def save_session(self, user_type, identifier, token):
        """Sauvegarder la session localement"""
        import json
        import time
    
        session_data = {
            'user_type': user_type,
            'identifier': identifier,
            'token': token,
            'timestamp': time.time()
        }
    
        try:
            with open('session.json', 'w') as f:
                json.dump(session_data, f)
            print(f"✅ Session sauvegardée dans session.json")
            print(f"   Type: {user_type}")
            print(f"   Identifiant: {identifier}")
            print(f"   Token: {token}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde session: {e}")        

    def go_to_register(self, instance):
        """Aller à l'écran d'inscription"""
        if "client_register" not in self.manager.screen_names:
            self.manager.add_widget(ClientRegisterScreen(name="client_register"))
        self.manager.current = "client_register"       

    def debug_api_client_state(self):
        """Afficher l'état actuel de l'API client"""
        global api_client, API_MODULE_EXISTS
    
        print("\n" + "="*50)
        print("🔍 ÉTAT API CLIENT - DEBUG")
        print("="*50)
    
        print(f"1. api_client existe: {api_client is not None}")
        print(f"2. API_MODULE_EXISTS: {API_MODULE_EXISTS}")
    
        if api_client:
            print(f"3. api_client.token: {getattr(api_client, 'token', 'NON DÉFINI')}")
            print(f"4. api_client.user_type: {getattr(api_client, 'user_type', 'NON DÉFINI')}")
            print(f"5. api_client.base_url: {getattr(api_client, 'base_url', 'NON DÉFINI')}")
        
            # Vérifier les attributs disponibles
            print(f"6. Attributs api_client: {[attr for attr in dir(api_client) if not attr.startswith('_')]}")
    
        from kivy.app import App
        app = App.get_running_app()
        print(f"7. app.client_data: {getattr(app, 'client_data', 'NON DÉFINI')}")
        print(f"8. app.telephone: {getattr(app, 'telephone', 'NON DÉFINI')}")
    
        print("="*50 + "\n")       

    def show_popup(self, title, message):
        """Afficher un popup d'information"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.popup import Popup
        from kivy.clock import Clock

        def show():
            content = BoxLayout(orientation="vertical", padding=10, spacing=10)
            content.add_widget(Label(text=message, halign="center"))

            btn_close = Button(
                text="OK", size_hint=(0.5, None), height=40, pos_hint={"center_x": 0.5}
            )

            popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))

            def close_popup(instance):
                popup.dismiss()

            btn_close.bind(on_press=close_popup)
            content.add_widget(btn_close)
            popup.open()

        Clock.schedule_once(lambda dt: show(), 0)
        


class ClientRegisterScreen(Screen):
    """Écran d'inscription client"""

    def __init__(self, **kwargs):
        super(ClientRegisterScreen, self).__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=40, spacing=25)

        # Titre
        title = Label(
            text="[b]Créer un compte ZAHEL[/b]",
            markup=True,
            font_size="24sp",
            halign="center",
        )

        # Nom
        self.txt_nom = TextInput(
            hint_text="Nom complet",
            multiline=False,
            size_hint=(1, None),
            height=50,
            font_size="16sp",
        )

        # Téléphone
        self.txt_phone = TextInput(
            hint_text="Numéro de téléphone (ex: +26934011111)",
            multiline=False,
            size_hint=(1, None),
            height=50,
            font_size="16sp",
        )

        # Mot de passe
        self.txt_password = TextInput(
            hint_text="Mot de passe",
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=50,
            font_size="16sp",
        )

        # Confirmation mot de passe
        self.txt_password_confirm = TextInput(
            hint_text="Confirmer le mot de passe",
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=50,
            font_size="16sp",
        )

        # Bouton inscription
        btn_register = Button(
            text="[size=18][b]CRÉER MON COMPTE[/b][/size]",
            markup=True,
            size_hint=(1, None),
            height=60,
            background_color=(0.2, 0.6, 0.2, 1),
        )
        btn_register.bind(on_press=self.register)

        # Bouton retour
        btn_back = Button(
            text="← Retour à la connexion",
            size_hint=(0.6, None),
            height=40,
            pos_hint={"center_x": 0.5},
        )
        btn_back.bind(on_press=self.go_back)

        layout.add_widget(title)
        layout.add_widget(self.txt_nom)
        layout.add_widget(self.txt_phone)
        layout.add_widget(self.txt_password)
        layout.add_widget(self.txt_password_confirm)
        layout.add_widget(btn_register)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def register(self, instance):
        """Inscription RÉELLE via API - VERSION CORRIGÉE"""
        nom = self.txt_nom.text.strip()
        phone = self.txt_phone.text.strip()
        password = self.txt_password.text.strip()
    
        if not nom or not phone or not password:
            self.show_popup("Erreur", "Tous les champs sont requis")
            return
    
        print(f"📝 Tentative inscription réelle: {nom} - {phone}")
    
        global api_client
        if api_client and hasattr(api_client, 'client_register'):
            try:
                result = api_client.client_register(nom, phone, password)
                print(f"📡 Réponse API: {result}")
            
                if result.get('success'):
                    self.show_popup(
                        "✅ Succès", 
                        f"Inscription réussie !\n\nVous pouvez maintenant vous connecter avec:\n{phone}"
                    )
                    # Redirection vers écran de connexion
                    self.manager.current = 'client_login'
                else:
                    error = result.get('error', 'Erreur inconnue')
                    self.show_popup("❌ Erreur", f"Inscription échouée:\n{error}")
                
            except Exception as e:
                print(f"❌ Exception inscription: {e}")
                self.show_popup("❌ Erreur", f"Exception: {str(e)}")
        else:
            print("⚠️ API non disponible, utilisation mode simulation")
            self.simulate_register(nom, phone, password)

    def simulate_register(self, nom, telephone, password):
        """Simulation d'inscription (uniquement si API hors ligne)"""
        print(f"🔄 Mode simulation - Inscription: {nom} - {telephone}")
    
        # Simulation uniquement pour test
        self.show_popup(
            "⚠️ Mode Test", 
            f"Inscription simulée pour {nom}\n\n"
            f"Téléphone: {telephone}\n"
            f"Mot de passe: {password}\n\n"
            f"⚠️ Ces données ne sont PAS enregistrées en base.\n"
            f"Pour une vraie inscription, assurez-vous que l'API est lancée."
        )
        self.manager.current = 'client_login'

    def go_back(self, instance):
        """Retour à la connexion"""
        self.manager.current = "client_login"

    def handle_register_result(self, result, button):
        """Gérer le résultat de l'inscription"""
        button.disabled = False
        button.text = "[size=18][b]CRÉER MON COMPTE[/b][/size]"

        if result.get("success"):
            print("✅ Inscription réussie!")
            self.show_popup(
                "Succès",
                "Compte créé avec succès!\nVous pouvez maintenant vous connecter.",
            )

            # Retour à la connexion après 2 secondes
            from kivy.clock import Clock

            Clock.schedule_once(
                lambda dt: setattr(self.manager, "current", "client_login"), 2
            )
        else:
            error_msg = result.get("error", "Erreur inconnue")
            print(f"❌ Erreur inscription: {error_msg}")
            self.show_popup("Erreur", f"Échec de l'inscription:\n{error_msg}")

    def show_popup(self, title, message):
        """Afficher un popup d'information"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
    
        popup = Popup(
            title=title,
            content=Label(text=message, halign='center'),
            size_hint=(0.8, 0.4)
        )
        popup.open()


# ==================== ÉCRAN DE CONNEXION ====================


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=40, spacing=20)

        # Logo/Titre
        title = Label(
            text="ZAHEL",
            font_size=36,
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=None,
            height=60,
        )

        subtitle = Label(
            text="Application Conducteur",
            font_size=16,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=30,
        )

        # Champs de connexion
        self.immatricule_input = TextInput(
            hint_text="Immatricule (ex : ZH-327KYM)",
            multiline=False,
            size_hint_y=None,
            height=50,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[10, 10],
        )

        self.password_input = TextInput(
            hint_text="Mot de passe",
            multiline=False,
            password=True,
            size_hint_y=None,
            height=50,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[10, 10],
        )

        # Bouton de connexion
        login_button = Button(
            text="SE CONNECTER",
            size_hint_y=None,
            height=50,
            bold=True,
            font_size=16,
            background_color=(0.2, 0.6, 0.2, 1),
        )
        login_button.bind(on_press=self.login)

        # Bouton inscription
        btn_register = Button(
            text="📝 Pas encore inscrit ? Créer un compte",
            size_hint_y=None,
            height=40,
            background_color=(0.3, 0.5, 0.7, 1),
            font_size=14,
        )
        btn_register.bind(on_press=self.go_to_register)

        # Message
        info = Label(
            text="Version 1.0 - © 2024 ZAHEL",
            font_size=12,
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=20,
        )

        # Ajouter tous les éléments
        self.layout.add_widget(title)
        self.layout.add_widget(subtitle)
        self.layout.add_widget(Label(size_hint_y=None, height=20))
        self.layout.add_widget(self.immatricule_input)
        self.layout.add_widget(self.password_input)
        self.layout.add_widget(login_button)
        self.layout.add_widget(btn_register) 
        self.layout.add_widget(Label(size_hint_y=None, height=20))
        self.layout.add_widget(info)

        self.add_widget(self.layout)

    def login(self, instance):
        # ✅ AJOUTE AU DÉBUT
        global api_client, API_MODULE_EXISTS

        immatricule = self.immatricule_input.text.strip()
        password = self.password_input.text.strip()

        print(f"🔐 Tentative de connexion: {immatricule}")

        if not immatricule or not password:
            print("❌ Champs vides")
            return

        # Initialiser le client API
        app = App.get_running_app()

        if API_MODULE_EXISTS:
            app.api_client = APIClient()
            # Connexion réelle
            try:
                result = app.api_client.login(immatricule, password)
                if result.get("success"):
                    print(f"✅ Connexion API réussie")
                    app.immatricule = immatricule
                    self.manager.current = "dashboard"
                    self.manager.get_screen("dashboard").update_data()
                else:
                    print(f"❌ Erreur connexion: {result.get('error')}")
            except Exception as e:
                print(f"❌ Erreur API: {e}")
                # Fallback à la simulation
                app.api_client = APIClientSimule()
                app.api_client.login(immatricule, password)
                app.immatricule = immatricule
                self.manager.current = "dashboard"
                self.manager.get_screen("dashboard").update_data()
        else:
            # Utilisation du client simulé
            app.api_client = APIClientSimule()
            app.api_client.login(immatricule, password)
            app.immatricule = immatricule
            self.manager.current = "dashboard"
            self.manager.get_screen("dashboard").update_data()

    def go_to_register(self, instance):
        """Aller à l'écran d'inscription conducteur"""
        print("📝 Redirection vers inscription conducteur")
    
        # Vérifier si l'écran existe déjà
        if "driver_register" not in self.manager.screen_names:
            print("⚠️ Écran driver_register non trouvé, ajout...")
            self.manager.add_widget(DriverRegisterScreen(name="driver_register"))
    
        self.manager.current = "driver_register"


class DriverRegisterScreen(Screen):
    """Écran d'inscription conducteur - SYSTÈME HYBRIDE WHATSAPP ZAHEL"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
        # CONTENEUR PRINCIPAL AVEC SCROLL
        root_layout = BoxLayout(orientation='vertical')
    
        # TITRE FIXE EN HAUT
        title = Label(
            text='[b]INSCRIPTION CONDUCTEUR ZAHEL[/b]',
            markup=True,
            size_hint_y=None,
            height=50,
            color=(0.2, 0.6, 1, 1)
        )
        root_layout.add_widget(title)
    
        # ZONE SCROLLABLE POUR LE FORMULAIRE
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
    
        # ===== SECTION 1 : INFORMATIONS PERSONNELLES =====
        layout.add_widget(Label(
            text='[u]INFORMATIONS PERSONNELLES[/u]',
            markup=True,
            size_hint_y=None,
            height=30,
            color=(0.8, 0.8, 0.8, 1)
        ))
    
        self.txt_nom = TextInput(
            hint_text='Nom complet',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.txt_nom)
    
        self.txt_telephone = TextInput(
            hint_text='Téléphone (ex: +26934012345)',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.txt_telephone)
    
        self.txt_password = TextInput(
            hint_text='Mot de passe',
            password=True,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.txt_password)
    
        self.txt_nationalite = TextInput(
            hint_text='Nationalité',
            size_hint_y=None,
            height=50,
            text='Comorienne'
        )
        layout.add_widget(self.txt_nationalite)
    
        self.txt_numero_identite = TextInput(
            hint_text='Numéro pièce d\'identité',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.txt_numero_identite)
    
        # ===== SECTION 2 : INFORMATIONS VÉHICULE =====
        layout.add_widget(Label(
            text='[u]INFORMATIONS VÉHICULE[/u]',
            markup=True,
            size_hint_y=None,
            height=30,
            color=(0.8, 0.8, 0.8, 1)
        ))
    
        # CATÉGORIE (Spinner)
        self.spinner_categorie = Spinner(
            text='standard',
            values=('standard', 'confort', 'luxe', 'moto'),
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.4, 0.8, 1)
        )
        self.spinner_categorie.bind(text=self.on_categorie_change)
        layout.add_widget(self.spinner_categorie)
    
        # MESSAGE D'INFO SELON CATÉGORIE
        self.lbl_info_categorie = Label(
            text='✅ Moto/Standard : Activation immédiate',
            size_hint_y=None,
            height=40,
            color=(0.2, 0.8, 0.2, 1),
            halign='center'
        )
        layout.add_widget(self.lbl_info_categorie)
    
        self.txt_marque = TextInput(
            hint_text='Marque (ex: Toyota)',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.txt_marque)
    
        self.txt_modele = TextInput(
            hint_text='Modèle (ex: Corolla)',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.txt_modele)
    
        self.txt_couleur = TextInput(
            hint_text='Couleur',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.txt_couleur)
    
        self.txt_plaque = TextInput(
            hint_text='Plaque d\'immatriculation',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.txt_plaque)
    
        # ===== BOUTON INSCRIPTION =====
        btn_inscrire = Button(
            text="✅ S'INSCRIRE",
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.8, 0.2, 1),
            font_size=18,
            bold=True
        )
        btn_inscrire.bind(on_press=self.inscrire_conducteur)
        layout.add_widget(btn_inscrire)
    
        # ===== BOUTON RETOUR =====
        btn_retour = Button(
            text="⬅ RETOUR",
            size_hint_y=None,
            height=50,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        btn_retour.bind(on_press=self.go_back)
        layout.add_widget(btn_retour)
    
        # AJOUTER LE LAYOUT SCROLLABLE
        scroll.add_widget(layout)
        root_layout.add_widget(scroll)
    
        self.add_widget(root_layout)
    
    def on_categorie_change(self, spinner, text):
        """Changer le message d'info selon la catégorie"""
        if text in ['confort', 'luxe']:
            self.lbl_info_categorie.text = '📱 VÉRIFICATION REQUISE - Envoyez vos documents sur WhatsApp'
            self.lbl_info_categorie.color = (1, 0.6, 0, 1)  # Orange
        else:
            self.lbl_info_categorie.text = '✅ Activation immédiate - Connectez-vous maintenant !'
            self.lbl_info_categorie.color = (0.2, 0.8, 0.2, 1)  # Vert
    
    def go_back(self, instance):
        """Retour à l'écran de connexion conducteur"""
        self.manager.current = 'driver_login'
    
    def ouvrir_whatsapp_verification(self, immatricule, categorie):
        """Ouvrir WhatsApp avec message pré-rempli pour vérification"""
        try:
            from config.whatsapp_config import WHATSAPP_CONFIG
            # 🔥 IMPORT DE LA FONCTION GLOBALE (plus besoin de "from main")
            global ouvrir_whatsapp
        
            numero = WHATSAPP_CONFIG['AGENCE_NUMBER']
        
            # Choisir le bon template
            if categorie in WHATSAPP_CONFIG['MESSAGE_TEMPLATE']:
                message = WHATSAPP_CONFIG['MESSAGE_TEMPLATE'][categorie].format(
                    immatricule=immatricule
                )
            else:
                message = f"Immatricule: {immatricule}\nCatégorie: {categorie}\nDocuments et photos ci-joints."
        
            print(f"📲 Tentative ouverture WhatsApp - Numéro: {numero}")
        
            # Ouvrir WhatsApp
            ouvrir_whatsapp(numero, message)
        
        except Exception as e:
            print(f"❌ Erreur WhatsApp: {e}")
            # 🔥 CORRECTION : numero est défini DANS le bloc try
            numero_local = "26934011111"  # Valeur par défaut
            self.show_popup(
                "📱 ENVOYEZ VOS DOCUMENTS",
                f"Immatricule: {immatricule}\n\nEnvoyez vos photos sur WhatsApp:\n+{numero_local}",
                success=True
            )
    
    def inscrire_conducteur(self, instance):
        """Envoyer l'inscription à l'API - VERSION HYBRIDE WHATSAPP"""
        
        # 1. VALIDATION DES CHAMPS
        if not self.txt_nom.text.strip():
            self.show_popup("Erreur", "Nom requis")
            return
        
        if not self.txt_telephone.text.strip():
            self.show_popup("Erreur", "Téléphone requis")
            return
        
        if not self.txt_password.text.strip():
            self.show_popup("Erreur", "Mot de passe requis")
            return
        
        if not self.txt_marque.text.strip():
            self.show_popup("Erreur", "Marque du véhicule requise")
            return
        
        if not self.txt_plaque.text.strip():
            self.show_popup("Erreur", "Plaque d'immatriculation requise")
            return
        
        # 2. PRÉPARER LES DONNÉES
        categorie = self.spinner_categorie.text
        
        data = {
            'nom': self.txt_nom.text.strip(),
            'telephone': self.txt_telephone.text.strip(),
            'password': self.txt_password.text.strip(),
            'nationalite': self.txt_nationalite.text.strip() or 'Comorienne',
            'numero_identite': self.txt_numero_identite.text.strip() or f"CNI-{self.txt_telephone.text[-6:]}",
            'categorie': categorie,
            'marque': self.txt_marque.text.strip(),
            'modele': self.txt_modele.text.strip(),
            'couleur': self.txt_couleur.text.strip() or 'Non spécifiée',
            'plaque': self.txt_plaque.text.strip().upper()
        }
        
        print(f"📤 Envoi inscription: {data['telephone']} - {categorie}")
        
        # 3. APPEL API
        global api_client, API_MODULE_EXISTS
        
        if API_MODULE_EXISTS and api_client:
            try:
                result = api_client.register_driver(data)
                
                if result and result.get('success'):
                    # ✅ SUCCÈS API
                    conducteur = result.get('conducteur', {})
                    immatricule = conducteur.get('immatricule', 'Inconnu')
                    verification_requise = conducteur.get('verification_requise', False)
                    
                    if verification_requise and categorie in ['confort', 'luxe']:
                        # 🔵 CONFORT / LUXE : Envoi WhatsApp obligatoire
                        message_succes = f"✅ INSCRIPTION SOUMISE !\n\nImmatricule: {immatricule}\n\n📱 ÉTAPE SUIVANTE:\nCliquez sur 'ENVOYER SUR WHATSAPP' pour envoyer vos photos et documents.\n\n⏳ Délai vérification: 2-4h"
                        
                        self.show_popup_verification(
                            immatricule, 
                            categorie, 
                            message_succes
                        )
                        
                    else:
                        # 🟢 MOTO / STANDARD : Activation immédiate
                        message_succes = f"✅ INSCRIPTION RÉUSSIE !\n\nImmatricule: {immatricule}\n\n👉 Vous pouvez vous connecter immédiatement et recevoir des courses !\n\nBienvenue dans la famille ZAHEL 🚗💨"
                        
                        self.show_popup("✅ Succès", message_succes, success=True)
                        
                        # Redirection vers connexion
                        from kivy.clock import Clock
                        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'driver_login'), 3)
                    
                else:
                    # ❌ ERREUR API
                    error_msg = result.get('error', 'Erreur inconnue')
                    self.show_popup("❌ Erreur", f"Inscription échouée: {error_msg}")
                    
            except Exception as e:
                print(f"❌ Exception inscription: {e}")
                self.show_popup("❌ Erreur", f"Erreur de connexion: {str(e)}")
        else:
            # MODE SIMULATION
            self.show_popup("🔧 Mode Simulation", "L'API n'est pas disponible. Mode démonstration activé.")
    
    def show_popup_verification(self, immatricule, categorie, message):
        """Popup spécial avec bouton WhatsApp pour vérification"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # MESSAGE
        lbl_message = Label(
            text=message,
            color=(0.2, 0.8, 0.2, 1),
            font_size=16,
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=200
        )
        lbl_message.bind(size=lbl_message.setter('text_size'))
        content.add_widget(lbl_message)
        
        # BOUTON WHATSAPP (ÉNORME ET COLORÉ)
        btn_whatsapp = Button(
            text="📱 ENVOYER SUR WHATSAPP",
            size_hint_y=None,
            height=70,
            background_color=(0.1, 0.8, 0.1, 1),  # Vert WhatsApp
            font_size=18,
            bold=True
        )
        btn_whatsapp.bind(on_press=lambda x: self.ouvrir_whatsapp_verification(immatricule, categorie))
        content.add_widget(btn_whatsapp)
        
        # BOUTON PLUS TARD
        btn_plus_tard = Button(
            text="⏳ Plus tard",
            size_hint_y=None,
            height=50,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        btn_plus_tard.bind(on_press=lambda x: self.after_verification(immatricule))
        content.add_widget(btn_plus_tard)
        
        popup = Popup(
            title="📋 VÉRIFICATION REQUISE",
            title_color=(1,1,1,1),
            title_size=18,
            title_align='center',
            content=content,
            size_hint=(0.9, 0.6),
            auto_dismiss=False
        )
        
        btn_plus_tard.bind(on_press=popup.dismiss)
        btn_whatsapp.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def after_verification(self, immatricule):
        """Après fermeture du popup"""
        from kivy.clock import Clock
        self.show_popup(
            "📱 ENVOYEZ VOS DOCUMENTS",
            f"Immatricule: {immatricule}\n\nEnvoyez vos photos sur WhatsApp.\nNous activons votre compte sous 2-4h.",
            success=True
        )
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'driver_login'), 3)
    
    def show_popup(self, title, message, success=False):
        """Popup standard"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        color = (0.2, 0.8, 0.2, 1) if success else (1, 0.4, 0.4, 1)
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl = Label(
            text=message,
            color=color,
            font_size=16,
            halign='center',
            valign='middle'
        )
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=50,
            background_color=(0.3, 0.6, 0.9, 1)
        )
        
        popup = Popup(
            title=title,
            title_color=(1,1,1,1),
            title_size=18,
            title_align='center',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        content.add_widget(btn_ok)
        popup.open()

# ==================== ÉCRAN DASHBOARD ====================

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        # ===== EN-TÊTE AVEC BADGE D'ABONNEMENT =====
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=60)

        # Label de bienvenue (à gauche)
        self.welcome_label = Label(
            text="Bonjour Conducteur", 
            font_size=18, 
            bold=True, 
            color=(0.2, 0.4, 0.8, 1),
            size_hint=(0.5, 1),
            halign='left'
        )

        # Conteneur pour le badge et le statut (à droite)
        right_box = BoxLayout(orientation="horizontal", size_hint=(0.5, 1), spacing=5)

        # ⭐ NOUVEAU : BADGE D'ABONNEMENT
        self.badge_label = Label(
            text="📦 --/50",
            font_size=14,
            bold=True,
            color=(0, 0.6, 0, 1),  # Vert par défaut
            size_hint=(0.4, 1),
            halign='right'
        )

        # Statut (disponible/indisponible)
        status_box = BoxLayout(orientation="vertical", size_hint=(0.3, 1))

        self.status_indicator = Label(
            text="●", font_size=24, color=(0, 1, 0, 1)  # Vert = disponible
        )

        self.status_text = Label(
            text="Dispo", font_size=10, color=(0.5, 0.5, 0.5, 1)
        )

        status_box.add_widget(self.status_indicator)
        status_box.add_widget(self.status_text)

        # ⭐ GARDER LE BADGE DE NOTIFICATIONS EXISTANT
        notifications_box = BoxLayout(orientation="vertical", size_hint_x=None, width=40)

        self.notification_badge = Label(
            text="",  # Vide par défaut
            font_size=16,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(20, 20)
        )

        self.notification_label = Label(
            text="🔔",
            font_size=14,
            size_hint_y=None,
            height=20
        )

        notifications_box.add_widget(self.notification_badge)
        notifications_box.add_widget(self.notification_label)

        # Assemblage du right_box
        right_box.add_widget(self.badge_label)        # Badge abonnement
        right_box.add_widget(status_box)              # Statut (● Dispo)
        right_box.add_widget(notifications_box)       # Notifications existantes

        # Assemblage final du header
        header.add_widget(self.welcome_label)
        header.add_widget(right_box)

        # Carte de statistiques
        stats_card = BoxLayout(
            orientation="vertical", size_hint_y=None, height=120, padding=15, spacing=10
        )

        # Fond gris pour la carte
        with stats_card.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Gris clair
            self.stats_bg = Rectangle(pos=stats_card.pos, size=stats_card.size)
            stats_card.bind(pos=self.update_bg, size=self.update_bg)

        stats_title = Label(
            text="VOS STATISTIQUES",
            font_size=14,
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=25,
        )

        stats_grid = BoxLayout(orientation="horizontal", size_hint_y=None, height=60)

        self.courses_count = Label(
            text="0\nCourses", font_size=18, bold=True, halign="center"
        )

        self.earnings_count = Label(
            text="0 KMF\nGains", font_size=18, bold=True, halign="center"
        )

        self.rating_count = Label(
            text="5.0\nNote", font_size=18, bold=True, halign="center"
        )

        stats_grid.add_widget(self.courses_count)
        stats_grid.add_widget(self.earnings_count)
        stats_grid.add_widget(self.rating_count)

        stats_card.add_widget(stats_title)
        stats_card.add_widget(stats_grid)

        self.amendes_stats_label = Label(
            text="",
            font_size=12,
            color=(0.8, 0.4, 0, 1),
            size_hint_y=None,
            height=20
        )

        # ===== ÉTIQUETTE DISCRÈTE DES TAXES =====
        self.taxes_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=30,
            padding=[10, 0, 10, 0]
        )

        self.taxes_label = Label(
            text="",  # Vide par défaut
            font_size=12,
            color=(0.6, 0.6, 0.6, 1),  # Gris discret
            halign='right'
        )

        self.taxes_box.add_widget(Label())  # Espaceur à gauche
        self.taxes_box.add_widget(self.taxes_label) 

        # Boutons d'action
        action_box = BoxLayout(
            orientation="vertical", spacing=10, size_hint_y=None, height=180
        )

        self.toggle_button = Button(
            text="DEVENIR INDISPONIBLE",
            size_hint_y=None,
            height=40,
            bold=True,
            background_color=(0.8, 0.2, 0.2, 1),  # Rouge
        )
        self.toggle_button.bind(on_press=self.toggle_status)

        courses_button = Button(
            text="VOIR LES COURSES",
            size_hint_y=None,
            height=40,
            bold=True,
            background_color=(0.2, 0.4, 0.8, 1),  # Bleu
        )
        courses_button.bind(on_press=self.show_courses)

        amendes_button = Button(
            text="MES AMENDES",
            size_hint_y=None,
            height=40,
            bold=True,
            background_color=(0.8, 0.2, 0.2, 1),  # Rouge
        )
        amendes_button.bind(on_press=self.show_amendes)

        profile_button = Button(
            text="MON PROFIL",
            size_hint_y=None,
            height=40,
            bold=True,
            background_color=(0.8, 0.5, 0.2, 1),  # Orange
        )
        profile_button.bind(on_press=self.show_profile)

        refresh_btn = Button(
            text="🔄",
            size_hint=(0.1, 0.05),
            pos_hint={"right": 0.95, "top": 0.95},
            background_color=(0.2, 0.4, 0.8, 1),
        )
        refresh_btn.bind(on_press=lambda x: self.update_data())
        self.layout.add_widget(refresh_btn)

        logout_button = Button(
            text="DÉCONNEXION",
            size_hint_y=None,
            height=40,
            bold=True,
            background_color=(0.8, 0.2, 0.2, 1),  # Rouge
        )
        logout_button.bind(on_press=self.logout)

        action_box.add_widget(self.toggle_button)
        action_box.add_widget(courses_button)
        action_box.add_widget(amendes_button)
        action_box.add_widget(profile_button)
        action_box.add_widget(logout_button)

        # Cours disponibles
        self.courses_label = Label(
            text="Aucune course disponible",
            font_size=14,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=40,
        )

        # Ajout final
        self.layout.add_widget(header)
        self.layout.add_widget(stats_card)
        self.layout.add_widget(self.taxes_box)
        self.layout.add_widget(action_box)
        self.layout.add_widget(self.courses_label)

        self.add_widget(self.layout)

    def update_bg(self, instance, value):
        """Met à jour le fond de la carte de statistiques"""
        self.stats_bg.pos = instance.pos
        self.stats_bg.size = instance.size

    def update_data(self):
        """Met à jour les données du dashboard - VERSION FINALE"""
        from kivy.app import App
        import requests
        import json

        app = App.get_running_app()

        print("\n" + "=" * 60)
        print("📊 DASHBOARD - MISE À JOUR DES STATISTIQUES")
        print("=" * 60)

        # 1. Mettre à jour le nom
        if hasattr(app, "immatricule"):
            immatricule = app.immatricule
            self.welcome_label.text = f"Bonjour {immatricule}"

            print(f"👤 Conducteur: {immatricule}")

            # 2. APPEL DIRECT À L'API (comme test_stats.py)
            try:
                API_BASE_URL = "http://localhost:5001"

                print(f"📡 Appel API: {API_BASE_URL}/api/conducteur/statistiques")

                response = requests.get(
                    f"{API_BASE_URL}/api/conducteur/statistiques",
                    headers={"Authorization": immatricule},
                    timeout=5,
                )

                print(f"📡 Status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()

                    # DEBUG: Voir la structure
                    print(f"✅ API success: {data.get('success')}")

                    if data.get("success"):
                        conducteur = data["conducteur"]
                        perf = conducteur.get("performance", {})
                        statut = conducteur.get("statut", {})

                        # Extraire les valeurs
                        courses = perf.get("courses_effectuees", 0)
                        gains = perf.get("gains_totaux", 0)
                        note = perf.get("note_moyenne", 5.0)
                        disponible = statut.get("disponible", True)
                        # ⭐ NOUVEAU : Récupérer les courses restantes
                        courses_restantes = perf.get("courses_restantes", 50)  # ou la clé exacte de ton API
                        print(f"   • Courses restantes: {courses_restantes}")
                        # Après avoir extrait courses_restantes et taxes_cumulees
                        taxes_cumulees = perf.get("taxes_cumulees", 0)

                        # ===== MISE À JOUR DE L'ÉTIQUETTE DES TAXES =====
                        if taxes_cumulees > 0:
                            self.taxes_label.text = f"🏷️ Taxes dues : {taxes_cumulees:,.0f} KMF"
                            self.taxes_label.color = (0.6, 0.6, 0.6, 1)  # Gris
                        else:
                            self.taxes_label.text = ""
                        # ===== MISE À JOUR DU BADGE D'ABONNEMENT =====
                        try:
                            # Mettre à jour le texte du badge
                            self.badge_label.text = f"📦 {courses_restantes}/50"
    
                            # Changer la couleur selon le niveau
                            if courses_restantes <= 0:
                                self.badge_label.color = (0.5, 0.5, 0.5, 1)  # Gris
                                self.badge_label.text = "📦 0/50"
                            elif courses_restantes <= 5:
                                self.badge_label.color = (1, 0, 0, 1)  # Rouge vif
                            elif courses_restantes <= 10:
                                self.badge_label.color = (1, 0.5, 0, 1)  # Orange
                            elif courses_restantes <= 20:
                                self.badge_label.color = (1, 0.8, 0, 1)  # Jaune/Orange clair
                            else:
                                self.badge_label.color = (0, 0.6, 0, 1)  # Vert
    
                            print(f"🏷️ Badge mis à jour: {courses_restantes}/50")
    
                        except Exception as e:
                            print(f"⚠️ Erreur mise à jour badge: {e}")
                            self.badge_label.text = "📦 --/50"

                        # ⭐ APPEL À LA NOUVELLE MÉTHODE
                        self.check_courses_restantes(courses_restantes)

                        print(f"📈 Données reçues:")
                        print(f"   • Courses: {courses}")
                        print(f"   • Gains: {gains:,.0f} KMF")
                        print(f"   • Note: {note}")
                        print(f"   • Disponible: {disponible}")

                        # 3. METTRE À JOUR L'INTERFACE
                        # A. Les statistiques
                        self.courses_count.text = f"{courses}\nCourses"
                        self.earnings_count.text = f"{gains:,.0f} KMF\nGains"
                        self.rating_count.text = f"{note:.1f}\nNote"

                        # Récupérer les stats des amendes
                        try:
                            stats_amendes = api_client.get_amendes_stats_conducteur()
                            if stats_amendes.get('success'):
                                a_verser = stats_amendes['stats']['a_verser']['total']
                                if a_verser > 0:
                                    self.amendes_stats_label.text = f"💰 Amendes à verser: {a_verser:,.0f} KMF"
                                    self.amendes_stats_label.color = (0.8, 0.4, 0, 1)
                                else:
                                    self.amendes_stats_label.text = ""
                        except:
                            pass

                        # B. Le statut (vert/rouge)
                        if disponible:
                            self.status_indicator.color = (0, 1, 0, 1)  # Vert
                            self.status_text.text = "Disponible"
                            self.toggle_button.text = "DEVENIR INDISPONIBLE"
                            self.toggle_button.background_color = (0.8, 0.2, 0.2, 1)
                            print(f"   • Statut: DISPONIBLE (vert)")
                        else:
                            self.status_indicator.color = (1, 0, 0, 1)  # Rouge
                            self.status_text.text = "Indisponible"
                            self.toggle_button.text = "DEVENIR DISPONIBLE"
                            self.toggle_button.background_color = (0.2, 0.6, 0.2, 1)
                            print(f"   • Statut: INDISPONIBLE (rouge)")

                        print(f"✅ Dashboard mis à jour avec succès!")

                    else:
                        error_msg = data.get("error", "Erreur inconnue")
                        print(f"❌ API error: {error_msg}")

                        # Fallback: valeurs par défaut
                        self.show_default_values()

                else:
                    print(f"❌ HTTP error: {response.status_code}")
                    print(f"   Response: {response.text[:100]}")

                    # Fallback: valeurs par défaut
                    self.show_default_values()

            except requests.exceptions.ConnectionError:
                print("❌ Impossible de se connecter à l'API")
                print("   Vérifie que le serveur backend tourne sur localhost:5001")
                self.show_default_values()

            except Exception as e:
                print(f"❌ Erreur inattendue: {e}")
                import traceback

                traceback.print_exc()
                self.show_default_values()

        else:
            print("⚠️  immatricule non trouvé")
            self.show_default_values()

        # 4. Vérifier les courses disponibles
        self.check_available_courses()

        print("=" * 60 + "\n")

    def copy_phone(self, phone_number):
        """Copier le numéro dans le presse-papier"""
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(phone_number)
    
        # Feedback visuel
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
    
        popup = Popup(
            title='📋 Copié',
            content=Label(text='Numéro copié dans le presse-papier'),
            size_hint=(0.6, 0.3)
        )
        popup.open()

    def show_default_values(self):
        """Afficher des valeurs par défaut si l'API échoue"""
        print("🔄 Utilisation valeurs par défaut")

        # Valeurs de fallback
        self.courses_count.text = "29\nCourses"  # Valeur actuelle de la base
        self.earnings_count.text = "35,635 KMF\nGains"
        self.rating_count.text = "5.0\nNote"

        # Statut par défaut: disponible
        self.status_indicator.color = (0, 1, 0, 1)  # Vert
        self.status_text.text = "Disponible"
        self.toggle_button.text = "DEVENIR INDISPONIBLE"
        self.toggle_button.background_color = (0.8, 0.2, 0.2, 1)

    def toggle_status(self, instance):
        # ✅ AJOUTE AU DÉBUT
        global api_client, API_MODULE_EXISTS

        """Bascule entre disponible/indisponible"""
        current_color = self.status_indicator.color

        if current_color == [0, 1, 0, 1]:  # Vert -> Rouge
            self.status_indicator.color = (1, 0, 0, 1)  # Rouge
            self.status_text.text = "Indisponible"
            self.toggle_button.text = "DEVENIR DISPONIBLE"
            self.toggle_button.background_color = (0.2, 0.6, 0.2, 1)  # Vert
            print("🔴 Statut: Indisponible")
        else:  # Rouge -> Vert
            self.status_indicator.color = (0, 1, 0, 1)  # Vert
            self.status_text.text = "Disponible"
            self.toggle_button.text = "DEVENIR INDISPONIBLE"
            self.toggle_button.background_color = (0.8, 0.2, 0.2, 1)  # Rouge
            print("🟢 Statut: Disponible")

        # Appeler l'API si disponible
        if hasattr(App.get_running_app(), "api_client"):
            try:
                app = App.get_running_app()
                disponible = self.status_indicator.color == [0, 1, 0, 1]
                app.api_client.toggle_status(disponible)
            except:
                pass

        self.check_available_courses()

    def check_available_courses(self):
        # ✅ AJOUTE AU DÉBUT
        global api_client, API_MODULE_EXISTS

        """Vérifie les courses disponibles depuis l'API"""
        if self.status_indicator.color == [0, 1, 0, 1]:  # Disponible
            try:
                app = App.get_running_app()
                if hasattr(app, "api_client"):
                    response = app.api_client.get_available_courses()
                    if response.get("success"):
                        count = response.get("count", 0)
                        if count > 0:
                            self.courses_label.text = (
                                f"🔔 {count} course(s) disponible(s)"
                            )
                            self.courses_label.color = (0.2, 0.6, 0.2, 1)  # Vert
                        else:
                            self.courses_label.text = "📭 Aucune course disponible"
                            self.courses_label.color = (0.5, 0.5, 0.5, 1)  # Gris
                    else:
                        self.courses_label.text = "⚠️ Erreur de connexion"
                        self.courses_label.color = (0.8, 0.5, 0.0, 1)  # Orange
            except Exception as e:
                print(f"❌ Erreur check_available_courses: {e}")
                # Fallback à la simulation
                courses = random.randint(0, 3)
                if courses > 0:
                    self.courses_label.text = f"🔔 {courses} course(s) disponible(s)"
                    self.courses_label.color = (0.2, 0.6, 0.2, 1)
                else:
                    self.courses_label.text = "📭 Aucune course disponible"
                    self.courses_label.color = (0.5, 0.5, 0.5, 1)
        else:
            self.courses_label.text = "⛔ Indisponible pour les courses"
            self.courses_label.color = (0.8, 0.2, 0.2, 1)  # Rouge

    def show_courses(self, instance):
        """Affiche l'écran des courses"""
        print("📋 Affichage des courses...")
        self.manager.current = "courses"

    def show_profile(self, instance):
        """Afficher le profil (avec option historique)"""
        print("👤 Affichage du profil...")
    
        # ✅ S'assurer que l'API client est dans l'app
        from kivy.app import App
        app = App.get_running_app()
    
        if hasattr(app, 'api_client') and app.api_client:
            print(f"   API client dans app: {app.api_client.token[:10]}...")
    
        if 'driver_profile' not in self.manager.screen_names:
            print("➕ Création de l'écran driver_profile...")
            self.manager.add_widget(DriverProfileScreen(name='driver_profile'))
    
        self.manager.current = 'driver_profile'

    def show_popup(self, title, message):
        """Afficher un popup d'information"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
    
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        lbl = Label(
            text=message,
            halign='center',
            valign='middle',
            font_size='16sp'
        )
        lbl.bind(size=lbl.setter('text_size'))
    
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 0.2, 1)
        )
    
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
    
        btn_ok.bind(on_press=popup.dismiss)
    
        content.add_widget(lbl)
        content.add_widget(btn_ok)
    
        popup.open()

    def logout(self, instance):
        """Déconnexion"""
        print("🚪 Déconnexion...")
        self.manager.current = "login"

    def manual_refresh(self, instance=None):
        """Rafraîchir manuellement les statistiques"""
        print("🔄 Rafraîchissement manuel demandé...")

        # Forcer le rafraîchissement
        self.update_data(force_refresh=True)

        # Afficher un feedback
        if hasattr(self, "refresh_label"):
            self.refresh_label.text = "🔄 Actualisé à " + time.strftime("%H:%M:%S")

        print("✅ Dashboard rafraîchi")

    def show_amendes(self, instance):
        """Affiche l'écran des amendes"""
        print("📋 Affichage des amendes...")
        self.manager.current = "amendes"

    def on_enter(self):
        """Quand l'écran s'affiche"""
        self.update_data()
        # Démarrer la vérification périodique des notifications
        Clock.schedule_interval(self.check_notifications, 30)  # Toutes les 30 secondes
    
    def on_leave(self):
        """Quand on quitte l'écran"""
        # Arrêter la vérification périodique
        Clock.unschedule(self.check_notifications)
    
    def check_notifications(self, dt=None):
        """Vérifie les nouvelles notifications"""
        print(f"🔔 Vérification des notifications... {time.strftime('%H:%M:%S')}")
        
        try:
            app = App.get_running_app()
            
            if hasattr(app, "api_client") and hasattr(app, "immatricule"):
                token = app.immatricule
                response = app.api_client.get_notifications_non_lues(token)
                
                if response.get('success'):
                    # ⭐ CORRECTION : Gérer l'attribut de manière sûre
                    old_count = 0
                    if hasattr(self, '_last_notification_count'):
                        old_count = self._last_notification_count
                    
                    new_count = response.get('count', 0)
                    
                    print(f"📱 Notifications non lues: {new_count} (précédent: {old_count})")
                    
                    # ⭐ SON SI NOUVELLE NOTIFICATION
                    if new_count > old_count and old_count == 0:
                        print("🔊 NOUVELLE NOTIFICATION !")
                        # Jouer un son (si activé)
                        self.play_notification_sound()
                    
                    # Sauvegarder pour la prochaine vérification
                    self._last_notification_count = new_count
                    
                    # Mettre à jour le badge
                    if new_count > 0:
                        self.notification_badge.text = str(new_count)
                        self.notification_label.text = "🔔"  # Sonnette
                        # ⭐ MODIFIÉ : Changer la couleur du texte directement
                        self.notification_badge.color = (1, 0, 0, 1)  # Rouge
                        self.notification_badge.bold = True
                        
                        # Si plus de 9 notifications, afficher "9+"
                        if new_count > 9:
                            self.notification_badge.text = "9+"
                        
                        # Si c'est une nouvelle notification, afficher popup
                        if new_count > old_count:
                            self.show_notification_alert(new_count)
                    else:
                        self.notification_badge.text = ""
                        self.notification_label.text = "🔕"  # Sonnette barrée
                        self.notification_badge.color = (0.5, 0.5, 0.5, 1)  # Gris
                        self.notification_badge.bold = False
                        
        except Exception as e:
            print(f"❌ Erreur vérification notifications: {e}")

    def play_notification_sound(self):
        """Joue un son de notification"""
        try:
            # Pour Windows
            import winsound
            # Fréquence 1000Hz, durée 300ms
            winsound.Beep(1000, 300)
            print("🔊 Son de notification joué")
        except ImportError:
            # Pour Linux/Mac ou si winsound non disponible
            try:
                import os
                # Son système simple
                print('\a')  # Caractère bell
            except:
                print("⚠️ Son non disponible sur ce système")
        except Exception as e:
            print(f"⚠️ Erreur son: {e}")

    def show_notification_alert(self, count):
        """Affiche une alerte pour nouvelles notifications"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation="vertical", padding=20, spacing=20)
        
        content.add_widget(Label(
            text="🔔 NOUVELLES COURSES !",
            font_size=20,
            bold=True,
            color=(0.2, 0.6, 0.2, 1)
        ))
        
        content.add_widget(Label(
            text=f"{count} nouvelle(s) course(s) disponible(s)",
            font_size=16
        ))
        
        # Boutons
        btn_box = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=50)
        
        voir_btn = Button(
            text="VOIR LES COURSES",
            background_color=(0.2, 0.6, 0.2, 1)
        )
        voir_btn.bind(on_press=lambda x: self.show_courses_and_close())
        
        ignorer_btn = Button(
            text="IGNORER",
            background_color=(0.8, 0.2, 0.2, 1)
        )
        
        btn_box.add_widget(voir_btn)
        btn_box.add_widget(ignorer_btn)
        
        content.add_widget(btn_box)
        
        self.notification_popup = Popup(
            title="",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        # Fermer la popup
        def close_popup(instance):
            self.notification_popup.dismiss()
        
        ignorer_btn.bind(on_press=close_popup)
        self.notification_popup.open()
    
    def show_courses_and_close(self):
        """Affiche les courses et ferme la popup"""
        if hasattr(self, 'notification_popup'):
            self.notification_popup.dismiss()
        self.show_courses(None)

    def check_courses_restantes(self, courses_restantes):
        """Vérifie et affiche un avertissement si les courses sont bientôt épuisées"""
    
        if courses_restantes <= 0:
            self.show_subscription_popup("❌ ABONNEMENT TERMINÉ", 
                "Votre abonnement est terminé.\n\nContactez l'agence ZAHEL pour recharger vos courses.")
            # Désactiver la disponibilité
            self.status_indicator.color = (1, 0, 0, 1)  # Rouge
            self.status_text.text = "Bloqué"
            self.toggle_button.disabled = True
        
        elif courses_restantes <= 3:
            if courses_restantes == 1:
                message = f"⚠️ DERNIÈRE COURSE INCLUSE !\n\nIl vous reste 1 course sur votre abonnement.\nPensez à recharger."
            else:
                message = f"⚠️ ATTENTION\n\nIl ne vous reste plus que {courses_restantes} courses incluses.\nContactez l'agence pour recharger."
        
            self.show_subscription_popup("Courses bientôt épuisées", message)
        
        elif courses_restantes <= 5:
            # Message discret dans le dashboard
            self.courses_label.text = f"⚠️ Plus que {courses_restantes} courses incluses"
            self.courses_label.color = (0.8, 0.5, 0, 1)  # Orange

    def show_subscription_popup(self, title, message):
        """Affiche un popup d'information sur l'abonnement"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
    
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        content.add_widget(Label(
            text=message,
            markup=True,
            halign='center',
            font_size='16sp'
        ))
    
        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=50)
    
        btn_ok = Button(text='OK', background_color=(0.2, 0.6, 0.2, 1))
        btn_contact = Button(text='📞 Contacter', background_color=(0.2, 0.5, 0.8, 1))
    
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
    
        def close_popup(instance):
            popup.dismiss()
    
        def contact_agence(instance):
            # Ouvrir WhatsApp ou téléphone
            import webbrowser
            webbrowser.open('https://wa.me/26934011111')
            popup.dismiss()
    
        btn_ok.bind(on_press=close_popup)
        btn_contact.bind(on_press=contact_agence)
    
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_contact)
        content.add_widget(btn_box)
    
        popup.open()

# ==================== ÉCRAN DES COURSES DISPONIBLES ====================


class CoursesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        # En-tête
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=60)

        back_btn = Button(
            text="← Retour",
            size_hint_x=None,
            width=100,
            background_color=(0.2, 0.4, 0.8, 1),
        )
        back_btn.bind(on_press=self.go_back)

        title = Label(
            text="COURSES DISPONIBLES",
            font_size=20,
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
        )

        refresh_btn = Button(
            text="🔄", size_hint_x=None, width=60, background_color=(0.2, 0.6, 0.2, 1)
        )
        refresh_btn.bind(on_press=self.refresh_courses)

        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(refresh_btn)

        # Liste des courses
        self.courses_list = ScrollView()
        self.courses_container = BoxLayout(
            orientation="vertical", spacing=10, size_hint_y=None
        )
        self.courses_container.bind(
            minimum_height=self.courses_container.setter("height")
        )
        self.courses_list.add_widget(self.courses_container)

        # Message par défaut
        self.default_label = Label(
            text="Chargement des courses...",
            font_size=16,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=100,
        )
        self.courses_container.add_widget(self.default_label)

        # Ajouter au layout
        self.layout.add_widget(header)
        self.layout.add_widget(self.courses_list)
        self.add_widget(self.layout)

    def go_back(self, instance):
        """Retour au dashboard"""
        print("🔙 Retour au dashboard...")
        self.manager.current = "dashboard"

    def refresh_courses(self, instance):
        """Rafraîchit la liste des courses"""
        print("🔄 Rafraîchissement des courses...")
        self.load_available_courses()

    def on_enter(self):
        """Chargé quand l'écran est affiché"""
        self.load_available_courses()

    def load_available_courses(self):
        # ✅ AJOUTE AU DÉBUT
        global api_client, API_MODULE_EXISTS

        """Charge les courses disponibles depuis l'API - VERSION OPTIMISÉE"""
        print("🔍 Chargement des courses disponibles...")

        # Vider la liste actuelle
        self.courses_container.clear_widgets()

        # Ajouter un indicateur de chargement
        loading_label = Label(
            text="Chargement des courses...",
            font_size=16,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=50,
        )
        self.courses_container.add_widget(loading_label)

        try:
            # Récupérer le client API
            app = App.get_running_app()

            if hasattr(app, "api_client"):
                response = app.api_client.get_available_courses_with_amendes()
                print(f"📥 Réponse API: {response.get('count', 0)} courses")

                # Retirer l'indicateur de chargement
                self.courses_container.clear_widgets()

                if response.get("success"):
                    courses = response.get("courses", [])
                    count = response.get("count", 0)

                    print(f"✅ {count} course(s) disponible(s)")

                    if count == 0:
                        self.courses_container.add_widget(
                            Label(
                                text="🎯 Aucune course disponible pour le moment",
                                font_size=16,
                                color=(0.5, 0.5, 0.5, 1),
                                size_hint_y=None,
                                height=100,
                            )
                        )

                        # Bouton de rafraîchissement
                        refresh_btn = Button(
                            text="🔄 Rafraîchir",
                            size_hint_y=None,
                            height=40,
                            background_color=(0.2, 0.4, 0.8, 1),
                        )
                        refresh_btn.bind(on_press=self.refresh_courses)
                        self.courses_container.add_widget(refresh_btn)
                    else:
                        for course in courses:
                            # ✅ APPEL SANS MARQUAGE INDIVIDUEL
                            self.add_course_card(course)
                else:
                    error_msg = response.get("error", "Erreur inconnue")
                    print(f"❌ Erreur API: {error_msg}")
                    self.courses_container.add_widget(
                        Label(
                            text=f"⚠️ Erreur: {error_msg}",
                            font_size=16,
                            color=(0.8, 0.2, 0.2, 1),
                            size_hint_y=None,
                            height=100,
                        )
                    )
            else:
                print("❌ API Client non disponible")
                self.courses_container.clear_widgets()
                self.courses_container.add_widget(
                    Label(
                        text="Client API non initialisé",
                        font_size=16,
                        color=(0.8, 0.2, 0.2, 1),
                        size_hint_y=None,
                        height=100,
                    )
                )

        except Exception as e:
            print(f"❌ Erreur chargement courses: {e}")
            self.courses_container.clear_widgets()
            self.courses_container.add_widget(
                Label(
                    text="💥 Impossible de contacter le serveur",
                    font_size=16,
                    color=(0.8, 0.2, 0.2, 1),
                    size_hint_y=None,
                    height=100,
                )
            )

    def add_course_card(self, course):
        """Ajoute une carte de course détaillée avec téléphone client (Variante B)"""
        print(f"🛠️ Création carte pour: {course.get('code')}")

        # Carte principale
        card = BoxLayout(
            orientation="vertical", 
            size_hint_y=None, 
            height=340,  # Assez haut pour toutes les infos
            padding=[15, 15, 15, 15], 
            spacing=8
        )

        # Fond blanc avec bord arrondi (simulé)
        with card.canvas.before:
            from kivy.graphics import Color, Rectangle
        
            # Fond blanc
            Color(1, 1, 1, 1)
            card_bg = Rectangle(pos=card.pos, size=card.size)
        
            # Bordure grise
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=(card.x, card.y), size=(card.width, 2))  # Haut
            Rectangle(pos=(card.x, card.y + card.height - 2), size=(card.width, 2))  # Bas
            Rectangle(pos=(card.x, card.y), size=(2, card.height))  # Gauche
            Rectangle(pos=(card.x + card.width - 2, card.y), size=(2, card.height))  # Droite

            def update_bg(instance, value):
                card_bg.pos = instance.pos
                card_bg.size = instance.size

            card.bind(pos=update_bg, size=update_bg)

        # ===== LIGNE 1 : Code + Âge de la course =====
        line1 = BoxLayout(size_hint=(1, 0.1))
    
        code_label = Label(
            text=f"🚖 [b]{course.get('code', 'N/A')}[/b]",
            markup=True,
            halign='left',
            font_size='15sp',
            size_hint=(0.7, 1),
            color=(0, 0, 0, 1)
        )
    
        # Âge de la course (simulé pour l'instant)
        import random
        age_min = random.randint(1, 8)
        if age_min > 5:
            age_color = (0.8, 0.2, 0.2, 1)  # Rouge si vieux
            age_text = f"⚠️ {age_min} min"
        else:
            age_color = (0.4, 0.4, 0.4, 1)  # Gris normal
            age_text = f"⏱️ {age_min} min"
    
        age_label = Label(
            text=f"[color={age_color[0]},{age_color[1]},{age_color[2]}]{age_text}[/color]",
            markup=True,
            halign='right',
            font_size='12sp',
            size_hint=(0.3, 1)
        )
    
        line1.add_widget(code_label)
        line1.add_widget(age_label)

        # ===== LIGNE 2 : Client (Nom + Note) =====
        client = course.get('client', {})
        client_nom = client.get('nom', 'Client')
        client_note = client.get('note_moyenne', 4.8)
        client_courses = client.get('courses_effectuees', 127)
    
        client_row = BoxLayout(size_hint=(1, 0.1))
    
        client_row.add_widget(Label(
            text=f"👤 [b]{client_nom}[/b]",
            markup=True,
            halign='left',
            font_size='14sp',
            size_hint=(0.6, 1),
            color=(0, 0, 0, 1)
        ))
    
        client_row.add_widget(Label(
            text=f"⭐ [b]{client_note}[/b] ({client_courses})",
            markup=True,
            halign='right',
            font_size='12sp',
            size_hint=(0.4, 1),
            color=(0.8, 0.5, 0, 1)
        ))

        # ===== LIGNE 3 : TÉLÉPHONE CLIENT (NOUVEAU) =====
        client_tel = client.get('telephone', '+269 XXX XXX')
    
        tel_row = BoxLayout(size_hint=(1, 0.1))
        tel_btn = Button(
            text=f"📞 [color=1565C0][b]{client_tel}[/b][/color]",
            markup=True,
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            size_hint=(1, 1),
            halign='left'
        )
        tel_btn.bind(on_press=lambda x: self.copy_phone(client_tel))
        tel_row.add_widget(tel_btn)

        # ===== LIGNE 4 : Itinéraire =====
        trajet_box = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=2)
    
        # Départ
        depart = course.get('depart', {})
        depart_adr = depart.get('adresse', 'Aéroport Moroni')
        if len(depart_adr) > 25:
            depart_adr = depart_adr[:22] + "..."
    
        trajet_box.add_widget(Label(
            text=f"🟢 [b]Départ:[/b] {depart_adr}",
            markup=True,
            halign='left',
            font_size='12sp',
            size_hint=(1, 0.5),
            color=(0, 0.5, 0, 1)
        ))
    
        # Arrivée
        arrivee = course.get('arrivee', {})
        arrivee_adr = arrivee.get('adresse', 'Hôtel Itsandra')
        if len(arrivee_adr) > 25:
            arrivee_adr = arrivee_adr[:22] + "..."
    
        trajet_box.add_widget(Label(
            text=f"🔴 [b]Arrivée:[/b] {arrivee_adr}",
            markup=True,
            halign='left',
            font_size='12sp',
            size_hint=(1, 0.5),
            color=(0.8, 0.2, 0.2, 1)
        ))

        # ===== LIGNE 5 : Stats course (Distance, Temps, Prix) =====
        stats_box = BoxLayout(size_hint=(1, 0.15), spacing=5)
    
        distance = course.get('distance_km', 8.5)
        duree = course.get('duree_estimee', 12)
        prix = course.get('prix_convenu', 0)
    
        # Distance
        stats_box.add_widget(Label(
            text=f"🛣️ [b]{distance} km[/b]",
            markup=True,
            font_size='13sp',
            size_hint=(0.33, 1),
            color=(0.3, 0.3, 0.3, 1)
        ))
    
        # Durée
        stats_box.add_widget(Label(
            text=f"⏱️ [b]{duree} min[/b]",
            markup=True,
            font_size='13sp',
            size_hint=(0.33, 1),
            color=(0.3, 0.3, 0.3, 1)
        ))
    
        # Prix (sans taxes)
        stats_box.add_widget(Label(
            text=f"💰 [b]{prix:,.0f} KMF[/b]",
            markup=True,
            font_size='15sp',
            size_hint=(0.34, 1),
            color=(0, 0.6, 0, 1)
        ))

        # ===== LIGNE 6 : Catégorie uniquement =====
        categorie = course.get('categorie', 'standard')
        cat_icons = {'standard': '🚗', 'confort': '✨', 'luxe': '⭐', 'moto': '🏍️'}
        cat_icon = cat_icons.get(categorie, '🚗')
    
        cat_row = BoxLayout(size_hint=(1, 0.1))
    
        cat_colors = {
            'standard': (0.3, 0.3, 0.3, 1),
            'confort': (0.8, 0.5, 0.2, 1),
            'luxe': (0.7, 0.2, 0.7, 1),
            'moto': (0.2, 0.5, 0.8, 1)
        }
        cat_color = cat_colors.get(categorie, (0.3, 0.3, 0.3, 1))
    
        cat_label = Label(
            text=f"{cat_icon} [b]{categorie.upper()}[/b]",
            markup=True,
            font_size='14sp',
            color=cat_color
        )
        cat_row.add_widget(cat_label)

        # ===== LIGNE 7 : BOUTON ACCEPTATION =====
        accept_btn = Button(
            text="[size=16][b]✅ ACCEPTER CETTE COURSE[/b][/size]",
            markup=True,
            size_hint=(1, 0.15),
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 0.2, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        accept_btn.bind(on_press=lambda x: self.accept_course(course))

        # ===== ASSEMBLAGE FINAL =====
        card.add_widget(line1)
        card.add_widget(client_row)
        card.add_widget(tel_row)  # ⭐ NOUVEAU : téléphone visible
        card.add_widget(trajet_box)
        card.add_widget(stats_box)
        card.add_widget(cat_row)
        card.add_widget(accept_btn)

        self.courses_container.add_widget(card)
        print(f"✅ Carte ajoutée pour {course.get('code')}")

    def accept_course(self, course):
        # ✅ AJOUTE AU DÉBUT
        global api_client, API_MODULE_EXISTS
        """Accepte une course et va à l'écran de navigation"""
        print(f"✅ Tentative d'acceptation: {course.get('code')}")

        try:
            # IMPORT en premier !
            from kivy.app import App

            # 1. Récupérer l'application
            app = App.get_running_app()

            # 2. Appeler l'API pour accepter la course
            if hasattr(app, "api_client"):
                response = app.api_client.accept_course(course["code"])

                if response.get("success"):
                    print("🎉 Course acceptée avec succès!")

                    # 3. Stocker la course dans l'application principale
                    app.current_course = course.get("code")

                    # 4. Aller à l'écran de navigation
                    if "navigation" in self.manager.screen_names:
                        self.manager.current = "navigation"
                    else:
                        print("❌ Écran navigation non trouvé, retour au dashboard")
                        self.manager.current = "dashboard"

                else:
                    error_msg = response.get("error", "Erreur inconnue")
                    print(f"❌ Erreur d'acceptation: {error_msg}")
                    self.show_error(f"Erreur: {error_msg}")

            else:
                print("❌ API client non disponible")
                self.show_error("Erreur: API non disponible")

        except Exception as e:
            print(f"❌ Exception accept_course: {e}")
            import traceback

            traceback.print_exc()

    def show_error(self, message):
        """Affiche un message d'erreur simple"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button

        content = BoxLayout(orientation="vertical", padding=20, spacing=20)
        content.add_widget(
            Label(text="❌ ERREUR", font_size=20, bold=True, color=(1, 0, 0, 1))
        )

        content.add_widget(Label(text=str(message), font_size=16))

        close_btn = Button(
            text="FERMER",
            size_hint_y=None,
            height=50,
            background_color=(0.8, 0.2, 0.2, 1),
        )

        popup = Popup(title="Erreur", content=content, size_hint=(0.7, 0.4))

        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def display_course_card(self, course):
        """Affiche une carte de course avec amende si présente"""
    
        # Créer le conteneur principal
        card = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=140 if course.get('amende_incluse') else 110,
            padding=[10, 5],
            spacing=5
        )
    
        # Style différent si amende
        if course.get('amende_incluse'):
            with card.canvas.before:
                Color(1, 0.9, 0.9, 1)  # Fond rose clair pour amende
                Rectangle(pos=card.pos, size=card.size)
        else:
            with card.canvas.before:
                Color(0.95, 0.95, 0.95, 1)  # Fond gris normal
                Rectangle(pos=card.pos, size=card.size)
    
        # Ligne 1: Trajet
        trajet_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
    
        depart_label = Label(
            text=f"[b]Départ:[/b] {course.get('depart_lat', 'N/A')}, {course.get('depart_lng', 'N/A')}",
            markup=True,
            size_hint_x=0.5,
            halign='left',
            text_size=(200, None)
        )
    
        arrivee_label = Label(
            text=f"[b]Arrivée:[/b] {course.get('arrivee_lat', 'N/A')}, {course.get('arrivee_lng', 'N/A')}",
            markup=True,
            size_hint_x=0.5,
            halign='left',
            text_size=(200, None)
        )
    
        trajet_box.add_widget(depart_label)
        trajet_box.add_widget(arrivee_label)
    
        # Ligne 2: Prix et distance
        info_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
    
        prix_text = f"[b]Prix:[/b] {course.get('prix_convenu', 0)} KMF"
    
        # ✅ AJOUTER L'INFO AMENDE SI PRÉSENTE
        if course.get('amende_incluse'):
            prix_text += f"\n[color=ff0000][b]+ Amende: {course['montant_amende']} KMF[/b][/color]"
    
        prix_label = Label(
            text=prix_text,
            markup=True,
            size_hint_x=0.5
        )
    
        distance_label = Label(
            text=f"[b]Distance:[/b] {course.get('distance_km', 'N/A')} km",
            markup=True,
            size_hint_x=0.5
        )
    
        info_box.add_widget(prix_label)
        info_box.add_widget(distance_label)
    
        # Ligne 3: Client et bouton
        action_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
    
        client_label = Label(
            text=f"[b]Client:[/b] {course.get('client', {}).get('nom', 'N/A')}",
            markup=True,
            size_hint_x=0.6
        )
    
        # ✅ NOUVEAU TEXTE BOUTON SI AMENDE
        btn_text = "ACCEPTER"
        if course.get('amende_incluse'):
            btn_text = f"ACCEPTER ({course['prix_total']} KMF)"
    
        accept_btn = Button(
            text=btn_text,
            size_hint_x=0.4,
            size_hint_y=None,
            height=25,
            background_color=(0.2, 0.6, 0.2, 1) if not course.get('amende_incluse') else (0.8, 0.3, 0.3, 1)
        )
    
        # Stocker le code de la course dans le bouton
        accept_btn.course_code = course['code']
        accept_btn.course_data = course  # Stocker toutes les données
        accept_btn.bind(on_press=self.accept_course)
    
        action_box.add_widget(client_label)
        action_box.add_widget(accept_btn)
    
        # Ajouter tout au card
        card.add_widget(trajet_box)
        card.add_widget(info_box)
        card.add_widget(action_box)
    
        # ✅ LIGNE SUPPLÉMENTAIRE POUR AMENDE
        if course.get('amende_incluse'):
            amende_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        
            amende_label = Label(
                text=f"[color=ff0000][b]⚠️ AMENDE À COLLECTER: {course['montant_amende']} KMF[/b][/color]",
                markup=True,
                size_hint_x=1,
                halign='center'
            )
        
            amende_box.add_widget(amende_label)
            card.add_widget(amende_box)
    
        return card


# ==================== ÉCRAN AMENDES COLLECTÉES ====================

class AmendesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        
        # Titre
        title = Label(
            text="[b]📋 AMENDES COLLECTÉES[/b]",
            font_size=20,
            markup=True,
            size_hint_y=None,
            height=50,
            color=(0.8, 0.2, 0.2, 1)
        )
        
        # Bouton rafraîchir
        refresh_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
        refresh_btn = Button(
            text="🔄 Rafraîchir",
            size_hint_x=0.3
        )
        refresh_btn.bind(on_press=self.load_amendes)
        
        # Statistiques
        self.stats_label = Label(
            text="Chargement...",
            size_hint_y=None,
            height=40
        )
        
        refresh_box.add_widget(refresh_btn)
        refresh_box.add_widget(self.stats_label)
        
        # Liste des amendes
        self.amendes_container = ScrollView()
        self.amendes_list = BoxLayout(
            orientation="vertical", 
            size_hint_y=None,
            spacing=10,
            padding=10
        )
        self.amendes_list.bind(minimum_height=self.amendes_list.setter('height'))
        
        self.amendes_container.add_widget(self.amendes_list)
        
        # Bouton retour
        back_btn = Button(
            text="← Retour au Dashboard",
            size_hint_y=None,
            height=40,
            background_color=(0.4, 0.4, 0.4, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        # Ajout final
        self.layout.add_widget(title)
        self.layout.add_widget(refresh_box)
        self.layout.add_widget(self.amendes_container)
        self.layout.add_widget(back_btn)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        """Quand l'écran est affiché"""
        global api_client
    
        print("📋 AmendesScreen - on_enter")
    
        from kivy.app import App
        app = App.get_running_app()
    
        if hasattr(app, 'api_client'):
            api_client = app.api_client
            print(f"   api_client récupéré depuis l'app")
    
        if not api_client or not api_client.token:
            self.amendes_list.clear_widgets()
            self.amendes_list.add_widget(Label(
            text="✅ Connecté\n\nAucune amende à collecter pour le moment",
                size_hint_y=None,
                height=100,
                color=(0, 0.6, 0, 1),
                halign='center'
            ))
            self.stats_label.text = "Aucune amende"
            return
    
        self.load_amendes()

    
    def load_amendes(self, instance=None):
        """Charge les amendes à collecter depuis l'API"""
        print("📋 Chargement des amendes à collecter...")
    
        # Vider la liste
        self.amendes_list.clear_widgets()
    
        # Ajouter indicateur de chargement
        loading = Label(
            text="Chargement des amendes...",
            size_hint_y=None,
            height=50,
            color=(0.5, 0.5, 0.5, 1)
        )
        self.amendes_list.add_widget(loading)
    
        global api_client
    
        if not api_client or not api_client.token:
            self.amendes_list.clear_widgets()
            self.amendes_list.add_widget(Label(
                text="❌ Non connecté",
                size_hint_y=None,
                height=50,
                color=(1, 0, 0, 1)
            ))
            return
    
        try:
            # Appel API pour récupérer les amendes à collecter
            response = api_client.get_amendes_a_collecter()
        
            self.amendes_list.clear_widgets()
        
            if response.get('success'):
                amendes = response.get('amendes', [])
                total = response.get('total_a_verser', 0)
            
                # Afficher le total
                total_label = Label(
                    text=f"[b]💰 TOTAL À VERSER: {total:,.0f} KMF[/b]",
                    markup=True,
                    size_hint_y=None,
                    height=50,
                    color=(0.2, 0.6, 0.2, 1)
                )
                self.amendes_list.add_widget(total_label)
            
                if not amendes:
                    self.amendes_list.add_widget(Label(
                        text="🎯 Aucune amende à collecter",
                        size_hint_y=None,
                        height=100,
                        color=(0.5, 0.5, 0.5, 1)
                    ))
                    return
            
                for amende in amendes:
                    self.add_amende_card(amende)
                
            else:
                self.amendes_list.add_widget(Label(
                    text=f"❌ Erreur: {response.get('error', 'Inconnue')}",
                    size_hint_y=None,
                    height=50,
                    color=(1, 0, 0, 1)
                ))
            
        except Exception as e:
            print(f"❌ Erreur chargement amendes: {e}")
            self.amendes_list.clear_widgets()
            self.amendes_list.add_widget(Label(
                text=f"💥 Erreur: {str(e)}",
                size_hint_y=None,
                height=50,
                color=(1, 0, 0, 1)
            ))
    
    def add_amende_card(self, amende):
        """Ajoute une carte d'amende à collecter"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=130,
            padding=15,
            spacing=5
        )
    
        # Fond coloré
        with card.canvas.before:
            Color(1, 0.95, 0.9, 1)  # Orange très clair
            card.rect = Rectangle(pos=card.pos, size=card.size)
    
        card.bind(pos=self.update_card_rect, size=self.update_card_rect)
    
        # Ligne 1: Montant et statut
        ligne1 = BoxLayout(size_hint_y=None, height=30)
    
        montant_label = Label(
            text=f"[b][color=e67e22]{amende['montant']:,.0f} KMF[/color][/b]",
            markup=True,
            halign='left',
            size_hint_x=0.5
        )
    
        statut_label = Label(
            text="[b]À VERSER[/b]",
            markup=True,
            color=(0.8, 0.4, 0, 1),
            halign='right',
            size_hint_x=0.5
        )
    
        ligne1.add_widget(montant_label)
        ligne1.add_widget(statut_label)
    
        # Ligne 2: Client et course
        client_label = Label(
            text=f"👤 {amende['client_nom']}",
            size_hint_y=None,
            height=20,
            halign='left'
        )
    
        course_label = Label(
            text=f"🚖 {amende['course_code']}",
            size_hint_y=None,
            height=20,
            halign='left'
        )
    
        # Ligne 3: Date et bouton
        ligne3 = BoxLayout(size_hint_y=None, height=40, spacing=10)
    
        date_label = Label(
            text=f"📅 {amende['date_collecte'][:10]}",
            size_hint_x=0.5,
            halign='left'
        )
    
        btn_verser = Button(
            text="💰 VERSER À L'AGENCE",
            size_hint_x=0.5,
            size_hint_y=None,
            height=35,
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        btn_verser.bind(on_press=lambda x, a=amende: self.confirmer_versement(a))
    
        ligne3.add_widget(date_label)
        ligne3.add_widget(btn_verser)
    
        card.add_widget(ligne1)
        card.add_widget(client_label)
        card.add_widget(course_label)
        card.add_widget(ligne3)
    
        self.amendes_list.add_widget(card)
    
    def confirmer_versement(self, amende):
        """Confirmer le versement d'une amende à l'agence"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
    
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        content.add_widget(Label(
            text=f"[b]CONFIRMER LE VERSEMENT[/b]",
            markup=True,
            size_hint_y=None,
            height=30
        ))
    
        content.add_widget(Label(
            text=f"Amende: {amende['montant']:,.0f} KMF\n"
                 f"Client: {amende['client_nom']}\n"
                 f"Course: {amende['course_code']}",
            halign='center'
        ))
    
        content.add_widget(Label(
            text="Confirmez-vous avoir versé cette somme à l'agence ?",
            color=(1, 0.5, 0, 1)
        ))
    
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
    
        btn_annuler = Button(
            text="Annuler",
            background_color=(0.8, 0.2, 0.2, 1)
        )
    
        btn_confirmer = Button(
            text="✅ CONFIRMER",
            background_color=(0.2, 0.6, 0.2, 1)
        )
    
        popup = Popup(
            title='Versement agence',
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
    
        def do_confirmer(instance):
            popup.dismiss()
            self.confirmer_versement_api(amende['id'])
    
        btn_annuler.bind(on_press=popup.dismiss)
        btn_confirmer.bind(on_press=do_confirmer)
    
        btn_layout.add_widget(btn_annuler)
        btn_layout.add_widget(btn_confirmer)
        content.add_widget(btn_layout)
    
        popup.open()


    def confirmer_versement_api(self, amende_chauffeur_id):
        """Appeler l'API pour confirmer le versement"""
        global api_client
    
        try:
            result = api_client.confirmer_collecte_amende(amende_chauffeur_id)
        
            if result.get('success'):
                self.show_popup("✅ Succès", result.get('message'))
                self.load_amendes()  # Recharger la liste
            else:
                self.show_popup("❌ Erreur", result.get('error', 'Erreur inconnue'))
            
        except Exception as e:
            self.show_popup("❌ Erreur", str(e))

    def go_back(self, instance):
        """Retour au dashboard"""
        self.manager.current = 'dashboard'

# ==================== ÉCRAN HISTORIQUE CONDUCTEUR ====================

class DriverHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # ===== EN-TÊTE =====
        header = BoxLayout(size_hint_y=None, height=50)
        
        btn_back = Button(
            text='←',
            size_hint_x=0.15,
            background_color=(0.2, 0.4, 0.8, 1)
        )
        btn_back.bind(on_press=self.go_back)
        
        title = Label(
            text='[b]📊 MON HISTORIQUE[/b]',
            markup=True,
            font_size='18sp',
            size_hint_x=0.7
        )
        
        header.add_widget(btn_back)
        header.add_widget(title)
        header.add_widget(Label(size_hint_x=0.15))  # Espace
        
        # ===== TOTAUX GLOBAUX =====
        self.totaux_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            padding=10,
            spacing=10
        )
        
        self.total_courses_label = Label(
            text='0\ncourses',
            font_size='14sp',
            bold=True,
            halign='center'
        )
        
        self.total_gains_label = Label(
            text='0 KMF\ngains',
            font_size='14sp',
            bold=True,
            color=(0, 0.6, 0, 1),
            halign='center'
        )
        
        self.total_taxes_label = Label(
            text='0 KMF\ntaxes',
            font_size='14sp',
            bold=True,
            color=(0.6, 0.6, 0.6, 1),
            halign='center'
        )
        
        self.totaux_box.add_widget(self.total_courses_label)
        self.totaux_box.add_widget(self.total_gains_label)
        self.totaux_box.add_widget(self.total_taxes_label)
        
        # ===== LISTE DÉROULANTE DES MOIS =====
        self.scroll = ScrollView(size_hint=(1, 1))
        self.history_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=8,
            padding=[0, 5, 0, 5]
        )
        self.history_container.bind(minimum_height=self.history_container.setter('height'))
        
        self.scroll.add_widget(self.history_container)
        
        # ===== BOUTON RAFRAÎCHIR =====
        btn_refresh = Button(
            text='🔄 Rafraîchir',
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.5, 0.8, 1)
        )
        btn_refresh.bind(on_press=self.load_history)
        
        # Assemblage
        self.layout.add_widget(header)
        self.layout.add_widget(self.totaux_box)
        self.layout.add_widget(self.scroll)
        self.layout.add_widget(btn_refresh)
        
        self.add_widget(self.layout)
    
    def go_back(self, instance):
        self.manager.current = 'driver_profile'
    
    def on_enter(self):
        """Quand on arrive sur l'écran"""
        print("=" * 60)
        print("📊 DriverHistoryScreen - on_enter")
        self.load_history()
        print("=" * 60)
    
    def load_history(self, instance=None):
        """Charger l'historique depuis l'API"""
        from kivy.app import App
        
        print("📊 Chargement de l'historique...")
        
        self.history_container.clear_widgets()
        
        # ✅ Récupérer l'API depuis l'application
        app = App.get_running_app()
        api_client = getattr(app, 'api_client', None)
        
        print(f"   api_client depuis app: {api_client}")
        
        if not api_client or not api_client.token:
            print(f"   ❌ Non connecté - token: {api_client.token if api_client else 'None'}")
            self.history_container.add_widget(Label(
                text="❌ Non connecté\n\nVeuillez vous reconnecter",
                size_hint_y=None,
                height=100,
                color=(1, 0, 0, 1)
            ))
            return
        
        # Ajouter indicateur de chargement
        loading = Label(
            text="🔄 Chargement...",
            size_hint_y=None,
            height=50,
            color=(0.5, 0.5, 0.5, 1)
        )
        self.history_container.add_widget(loading)
        
        try:
            print(f"   Appel API avec token: {api_client.token[:10]}...")
            result = api_client.get_conducteur_historique()
            
            self.history_container.clear_widgets()
            
            if result.get('success'):
                historique = result.get('historique', [])
                totaux = result.get('totaux', {})
                
                # Mettre à jour les totaux
                self.total_courses_label.text = f"{totaux.get('courses', 0)}\ncourses"
                self.total_gains_label.text = f"{totaux.get('gains', 0):,.0f} KMF\ngains"
                self.total_taxes_label.text = f"{totaux.get('taxes', 0):,.0f} KMF\ntaxes"
                
                if not historique:
                    self.history_container.add_widget(Label(
                        text="📭 Aucune donnée d'historique",
                        size_hint_y=None,
                        height=100,
                        color=(0.5, 0.5, 0.5, 1)
                    ))
                    return
                
                # Afficher chaque mois
                for mois_data in historique:
                    self.add_month_card(mois_data)
            else:
                error = result.get('error', 'Erreur inconnue')
                self.history_container.add_widget(Label(
                    text=f"❌ {error}",
                    size_hint_y=None,
                    height=50,
                    color=(1, 0, 0, 1)
                ))
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            self.history_container.clear_widgets()
            self.history_container.add_widget(Label(
                text=f"💥 {str(e)}",
                size_hint_y=None,
                height=50,
                color=(1, 0, 0, 1)
            ))
    
    def add_month_card(self, mois_data):
        """Ajouter une carte pour un mois"""
        # Formater le mois
        try:
            annee, mois_num = mois_data['mois'].split('-')
            mois_noms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            mois_nom = mois_noms[int(mois_num) - 1]
            mois_affichage = f"{mois_nom} {annee}"
        except:
            mois_affichage = mois_data['mois']
        
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=90,
            padding=10,
            spacing=5
        )
        
        # Fond gris clair
        with card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            card.rect = Rectangle(pos=card.pos, size=card.size)
        
        card.bind(pos=self.update_rect, size=self.update_rect)
        
        # Ligne 1: Mois
        mois_label = Label(
            text=f"[b]{mois_affichage}[/b]",
            markup=True,
            size_hint_y=None,
            height=20,
            halign='left',
            color=(0.2, 0.4, 0.8, 1)
        )
        
        # Ligne 2: Statistiques
        stats_line = BoxLayout(size_hint_y=None, height=25, spacing=5)
        
        stats_line.add_widget(Label(
            text=f"📊 {mois_data['courses']} courses",
            font_size='12sp',
            halign='left'
        ))
        
        stats_line.add_widget(Label(
            text=f"💰 {mois_data['gains']:,.0f} KMF",
            font_size='12sp',
            color=(0, 0.6, 0, 1)
        ))
        
        stats_line.add_widget(Label(
            text=f"🏷️ {mois_data['taxes']:,.0f} KMF",
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1)
        ))
        
        card.add_widget(mois_label)
        card.add_widget(stats_line)
        
        self.history_container.add_widget(card)
    
    def update_rect(self, instance, value):
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

class DriverProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # ===== EN-TÊTE =====
        header = BoxLayout(size_hint_y=None, height=50)
        
        btn_back = Button(
            text='← Retour',
            size_hint_x=0.3,
            background_color=(0.2, 0.4, 0.8, 1)
        )
        btn_back.bind(on_press=self.go_back)
        
        title = Label(
            text='[b]👤 MON PROFIL[/b]',
            markup=True,
            font_size='18sp',
            size_hint_x=0.7
        )
        
        header.add_widget(btn_back)
        header.add_widget(title)
        
        # ===== INFOS PERSONNELLES =====
        info_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=150,
            padding=15,
            spacing=10
        )
        
        with info_card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            Rectangle(pos=info_card.pos, size=info_card.size)
        
        self.lbl_immatricule = Label(
            text='Immatricule: --',
            font_size='16sp',
            bold=True,
            halign='left',
            size_hint_y=None,
            height=25
        )
        
        self.lbl_nom = Label(
            text='Nom: --',
            halign='left',
            size_hint_y=None,
            height=25
        )
        
        self.lbl_telephone = Label(
            text='Téléphone: --',
            halign='left',
            size_hint_y=None,
            height=25
        )
        
        self.lbl_vehicule = Label(
            text='Véhicule: --',
            halign='left',
            size_hint_y=None,
            height=25
        )
        
        info_card.add_widget(self.lbl_immatricule)
        info_card.add_widget(self.lbl_nom)
        info_card.add_widget(self.lbl_telephone)
        info_card.add_widget(self.lbl_vehicule)
        
        # ===== MENU OPTIONS =====
        menu_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=150)
        
        btn_history = Button(
            text='📊 Voir mon historique',
            size_hint_y=None,
            height=45,
            background_color=(0.3, 0.5, 0.7, 1)
        )
        btn_history.bind(on_press=self.go_to_history)
        
        btn_stats = Button(
            text='📈 Statistiques détaillées',
            size_hint_y=None,
            height=45,
            background_color=(0.3, 0.5, 0.7, 1)
        )
        btn_stats.bind(on_press=self.go_to_history)  # Redirige vers historique
        
        btn_renouveler = Button(
            text='🔄 Renouveler abonnement',
            size_hint_y=None,
            height=45,
            background_color=(0.2, 0.6, 0.2, 1)
        )
        btn_renouveler.bind(on_press=self.renouveler_abonnement)
        
        menu_box.add_widget(btn_history)
        menu_box.add_widget(btn_stats)
        menu_box.add_widget(btn_renouveler)
        
        self.layout.add_widget(header)
        self.layout.add_widget(info_card)
        self.layout.add_widget(menu_box)
        self.layout.add_widget(Label())  # Espace
        
        self.add_widget(self.layout)
        
        # Charger les infos
        Clock.schedule_once(self.load_driver_profile, 0.5)
    
    def on_enter(self):
        """Recharger à chaque entrée"""
        print("👤 DriverProfileScreen.on_enter")
        self.load_driver_profile()
    
    def load_driver_profile(self, dt=None):
        """Charger les infos du conducteur - VERSION FINALE"""
        from kivy.app import App
    
        print("\n" + "="*60)
        print("👤 CHARGEMENT PROFIL CONDUCTEUR")
        print("="*60)
    
        # Récupérer l'API client depuis l'application
        app = App.get_running_app()
        api_client = getattr(app, 'api_client', None)
    
        # Immatricule
        if hasattr(app, 'immatricule') and app.immatricule:
            immatricule = app.immatricule
            self.lbl_immatricule.text = f'[b]Immatricule:[/b] {immatricule}'
            self.lbl_immatricule.markup = True
            print(f"📌 Immatricule: {immatricule}")
    
        print(f"🔍 API Client depuis app: {api_client}")
    
        if api_client and api_client.token:
            print(f"🔍 Token trouvé: {api_client.token[:10]}...")
        
            try:
                result = api_client.get_conducteur_info()
            
                if result.get('success'):
                    conducteur = result.get('conducteur', {})
                
                    # Nom
                    nom = conducteur.get('nom', 'Inconnu')
                    self.lbl_nom.text = f'[b]Nom:[/b] {nom}'
                    self.lbl_nom.markup = True
                
                    # Téléphone (nouveau)
                    telephone = conducteur.get('telephone', 'Non renseigné')
                    self.lbl_telephone.text = f'[b]Téléphone:[/b] {telephone}'
                    self.lbl_telephone.markup = True
                
                    # Véhicule (nouveau)
                    vehicule = conducteur.get('vehicule', {})
                    marque = vehicule.get('marque', '')
                    modele = vehicule.get('modele', '')
                    couleur = vehicule.get('couleur', '')
                    plaque = vehicule.get('plaque', '')
                
                    vehicule_text = f"{couleur} {marque} {modele}".strip()
                    if not vehicule_text:
                        vehicule_text = "Non renseigné"
                
                    self.lbl_vehicule.text = f'[b]Véhicule:[/b] {vehicule_text}'
                    self.lbl_vehicule.markup = True
                
                    print(f"✅ Données chargées:")
                    print(f"   - Nom: {nom}")
                    print(f"   - Téléphone: {telephone}")
                    print(f"   - Véhicule: {vehicule_text}")
                
                else:
                    error = result.get('error', 'Erreur inconnue')
                    print(f"❌ Erreur API: {error}")
                
            except Exception as e:
                print(f"❌ Exception: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ API non disponible ou non authentifié")
    
        print("="*60 + "\n")
    
    def go_back(self, instance):
        self.manager.current = 'dashboard'
    
    def go_to_history(self, instance):
        """Aller à l'écran d'historique"""
        print("📊 Redirection vers historique")
        if 'driver_history' not in self.manager.screen_names:
            self.manager.add_widget(DriverHistoryScreen(name='driver_history'))
        self.manager.current = 'driver_history'
    
    def renouveler_abonnement(self, instance):
        """Renouveler l'abonnement"""
        self.show_popup(
            "Renouvellement",
            "Veuillez vous rendre à l'agence ZAHEL\npour renouveler votre abonnement."
        )
    
    def show_popup(self, title, message):
        """Afficher un popup"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        lbl = Label(
            text=message,
            halign='center',
            valign='middle',
            font_size='16sp'
        )
        lbl.bind(size=lbl.setter('text_size'))
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 0.2, 1)
        )
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        
        content.add_widget(lbl)
        content.add_widget(btn_ok)
        
        popup.open()


# ============= NOUVELLE VERSION AVEC CARTE =============
from kivy_garden.mapview import MapView, MapMarker
from kivy.clock import Clock
import threading
import time


class NavigationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.course_code = None
        self.course_data = None
        self.map_view = None
        self.is_navigating = False
        self.data_saver_mode = True

        # Marqueurs
        self.driver_marker = None
        self.client_marker = None
        self.destination_marker = None

        # Coordonnées (Moroni, Comores)
        self.driver_pos = (-11.698, 43.256)  # Position initiale conducteur
        self.client_pos = (-11.704, 43.261)  # Point de prise en charge
        self.dest_pos = (-11.710, 43.265)  # Destination

        # Données navigation
        self.current_phase = 0  # 0=vers client, 1=vers destination
        self.nav_progress = 0.0

        # AJOUTE CETTE LIGNE :
        self.build_interactive_interface()

        print("🗺️  NavigationScreen initialisée AVEC interface")

    def on_pre_enter(self):
        """Avant d'entrer dans l'écran"""
        from kivy.app import App

        app = App.get_running_app()
        self.course_code = getattr(app, "current_course", None)

        if self.course_code:
            print(f"🗺️  Navigation: {self.course_code}")
            self.load_course_data()

        # Construire l'interface
        self.build_interactive_interface()

        self.start_comores_preloading()

        # Démarrer après un court délai
        from kivy.clock import Clock

        Clock.schedule_once(self.start_interactive_navigation, 0.5)

    def build_interactive_interface(self):
        """Interface avec carte interactive"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.progressbar import ProgressBar

        # Layout principal
        main_layout = BoxLayout(orientation="vertical", padding=5, spacing=5)

        # 1. Header avec infos
        header = BoxLayout(size_hint_y=0.08, spacing=10)

        self.course_label = Label(
            text=f'[b]{self.course_code or "ZAHEL"}[/b]',
            markup=True,
            font_size="16sp",
            halign="left",
        )

        self.status_label = Label(
            text="[color=FF9900]● PRÉPARATION[/color]",
            markup=True,
            font_size="14sp",
            halign="right",
        )

        header.add_widget(self.course_label)
        header.add_widget(self.status_label)

        # 2. CONTAINER POUR LA CARTE (important !)
        self.map_container = BoxLayout(size_hint_y=0.65)

        # 3. Informations de navigation
        info_box = BoxLayout(size_hint_y=0.12, orientation="vertical", spacing=2)

        self.distance_label = Label(text="Distance: -- km", font_size="14sp", bold=True)

        self.time_label = Label(text="Temps: -- min", font_size="12sp")

        self.progress_bar = ProgressBar(max=100, size_hint_y=0.3, value=0)

        info_box.add_widget(self.distance_label)
        info_box.add_widget(self.time_label)
        info_box.add_widget(self.progress_bar)

        # 4. Instructions
        self.instruction_label = Label(
            text="Initialisation de la navigation...",
            font_size="14sp",
            color=(0, 0.4, 0.8, 1),
            size_hint_y=0.08,
            halign="center",
        )

        # 5. Boutons de contrôle
        controls = BoxLayout(size_hint_y=0.07, spacing=5)

        self.btn_zoom_in = Button(
            text="+", size_hint_x=0.15, background_color=(0.4, 0.4, 0.4, 1)
        )
        self.btn_zoom_in.bind(on_press=lambda x: self.zoom_map(1))

        self.btn_zoom_out = Button(
            text="-", size_hint_x=0.15, background_color=(0.4, 0.4, 0.4, 1)
        )
        self.btn_zoom_out.bind(on_press=lambda x: self.zoom_map(-1))

        self.btn_center = Button(
            text="↻", size_hint_x=0.15, background_color=(0.4, 0.4, 0.4, 1)
        )
        self.btn_center.bind(on_press=lambda x: self.center_map())

        self.btn_nav = Button(
            text="▶ DÉMARRER",
            size_hint_x=0.55,
            background_color=(0, 0.6, 0.2, 1),
            bold=True,
        )
        self.btn_nav.bind(on_press=self.toggle_navigation)

        self.btn_data_saver = Button(
            text="🌱 ECO",
            size_hint_x=0.15,
            background_color=(
                (0.2, 0.7, 0.2, 1) if self.data_saver_mode else (0.5, 0.5, 0.5, 1)
            ),
        )
        self.btn_data_saver.bind(on_press=self.toggle_data_saver)

        self.btn_route = Button(
            text="🗺️ ITINÉRAIRE", size_hint_x=0.2, background_color=(0.4, 0.2, 0.8, 1)
        )
        self.btn_route.bind(on_press=lambda x: self.draw_navigation_line())

        controls.add_widget(self.btn_zoom_in)
        controls.add_widget(self.btn_zoom_out)
        controls.add_widget(self.btn_center)
        controls.add_widget(self.btn_data_saver)
        controls.add_widget(self.btn_route)
        controls.add_widget(self.btn_nav)

        # Assembler tout
        main_layout.add_widget(header)
        main_layout.add_widget(self.map_container)
        main_layout.add_widget(info_box)
        main_layout.add_widget(self.instruction_label)
        main_layout.add_widget(controls)

        self.add_widget(main_layout)
        print("✅ Interface interactive construite")

        # Initialiser la carte
        Clock.schedule_once(self.init_real_map, 0.1)

    def toggle_data_saver(self, instance):
        """Activer/désactiver le mode économie de données"""
        # Alterner
        self.data_saver_mode = not getattr(self, "data_saver_mode", True)

        # Mettre à jour le bouton
        if self.data_saver_mode:
            self.btn_data_saver.background_color = (0.2, 0.7, 0.2, 1)
            self.btn_data_saver.text = "🌱 ECO"
            print("✅ Mode économie ACTIVÉ")

            # Appliquer les restrictions
            if self.map_view:
                self.map_view.double_tap_zoom = False
                self.map_view.touch_zoom = False
                self.map_view.zoom_max = 16

        else:
            self.btn_data_saver.background_color = (0.5, 0.5, 0.5, 1)
            self.btn_data_saver.text = "🌐 FULL"
            print("✅ Mode économie DÉSACTIVÉ")

            # Retirer les restrictions
            if self.map_view:
                self.map_view.double_tap_zoom = True
                self.map_view.touch_zoom = True
                self.map_view.zoom_max = 19

        # Mettre à jour les instructions
        if hasattr(self, "instruction_label"):
            if self.data_saver_mode:
                self.instruction_label.text = "Mode économie activé - Cache prioritaire"
            else:
                self.instruction_label.text = "Mode haute qualité - Données mobiles"

    def init_real_map(self, dt):
        """Initialiser la carte OpenStreetMap avec CACHE et MARQUEURS VISIBLES"""
        try:
            from kivy_garden.mapview import MapView, MapMarker
            import os

            print("🗺️  Initialisation carte PROFESSIONNELLE...")

            # 1. Vider le container
            self.map_container.clear_widgets()

            # 2. Créer le dossier de cache
            cache_dir = os.path.join(os.getcwd(), "cache", "osm_tiles_comores")
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
                print(f"📁 Cache: {cache_dir}")

            # 3. IMPORTANT: Charger les chemins ABSOLUS des icônes
            base_dir = os.path.join(os.getcwd(), "zahel_mobile")
            car_icon = (
                os.path.join(base_dir, "assets", "car_blue.png")
                if hasattr(self, "assets_path")
                else None
            )
            person_icon = (
                os.path.join(base_dir, "assets", "person_red.png")
                if hasattr(self, "assets_path")
                else None
            )
            flag_icon = (
                os.path.join(base_dir, "assets", "flag_green.png")
                if hasattr(self, "assets_path")
                else None
            )

            # Vérifier l'existence
            icons_exist = all(
                [
                    os.path.exists(icon)
                    for icon in [car_icon, person_icon, flag_icon]
                    if icon
                ]
            )
            print(f"🎯 Icônes existent: {icons_exist}")

            # 4. Créer la carte AVEC timeout augmenté
            self.map_view = MapView(
                zoom=14,  # Zoom plus large pour voir les 3 points
                lat=-11.698,  # Moroni centre
                lon=43.256,
                size_hint=(1, 1),
                cache_dir=cache_dir,
                # Ajouter ces options pour stabilité
                double_tap_zoom=True,
                snap_to_zoom=True,
            )

            # 5. AJOUTER LES MARQUEURS IMMÉDIATEMENT (avant d'ajouter la carte)
            print("📍 Ajout des marqueurs...")

            # Marqueur CONDUCTEUR (VOITURE)
            self.driver_marker = MapMarker(
                lat=self.driver_pos[0], lon=self.driver_pos[1]
            )
            if icons_exist and car_icon:
                try:
                    self.driver_marker.source = car_icon
                    print(f"   ✅ Voiture: {os.path.basename(car_icon)}")
                except:
                    print("   ⚠️  Échec chargement icône voiture")

            # Marqueur CLIENT (PERSONNE)
            self.client_marker = MapMarker(
                lat=self.client_pos[0], lon=self.client_pos[1]
            )
            if icons_exist and person_icon:
                try:
                    self.client_marker.source = person_icon
                    print(f"   ✅ Client: {os.path.basename(person_icon)}")
                except:
                    print("   ⚠️  Échec chargement icône client")

            # Marqueur DESTINATION (DRAPEAU)
            self.destination_marker = MapMarker(
                lat=self.dest_pos[0], lon=self.dest_pos[1]
            )
            if icons_exist and flag_icon:
                try:
                    self.destination_marker.source = flag_icon
                    print(f"   ✅ Destination: {os.path.basename(flag_icon)}")
                except:
                    print("   ⚠️  Échec chargement icône destination")

            # 6. CONFIGURATION DES MARQUEURS (CRITIQUE!)
            for marker in [
                self.driver_marker,
                self.client_marker,
                self.destination_marker,
            ]:
                if marker:
                    marker.allow_stretch = True  # Permettre l'étirement
                    marker.keep_ratio = True  # Garder les proportions
                    marker.size = (
                        (40, 40) if hasattr(marker, "size") else None
                    )  # Taille

            # 7. AJOUTER LES MARQUEURS À LA CARTE
            self.map_view.add_marker(self.driver_marker)
            self.map_view.add_marker(self.client_marker)
            self.map_view.add_marker(self.destination_marker)

            # 8. Centrer la carte sur la zone
            center_lat = (
                self.driver_pos[0] + self.client_pos[0] + self.dest_pos[0]
            ) / 3
            center_lon = (
                self.driver_pos[1] + self.client_pos[1] + self.dest_pos[1]
            ) / 3
            self.map_view.center_on(center_lat, center_lon)

            # 9. Ajouter la carte AU CONTAINER (en dernier!)
            self.map_container.add_widget(self.map_view)

            # 10. Vérifier visuellement
            print("✅ Carte professionnelle initialisée")
            print(f"   Marqueurs: 3 ajoutés")
            print(f"   Position: ({self.driver_pos[0]:.4f}, {self.driver_pos[1]:.4f})")

            # 11. Mode économie si activé
            if self.data_saver_mode:
                print("🌱 Mode économie activé")
                if hasattr(self.map_view, "double_tap_zoom"):
                    self.map_view.double_tap_zoom = False
                if hasattr(self.map_view, "touch_zoom"):
                    self.map_view.touch_zoom = False

            # 12. DEBUG: Vérifier que tout est bien positionné
            print(f"🔍 Positions finales:")
            print(
                f"   Conducteur: ({self.driver_marker.lat:.6f}, {self.driver_marker.lon:.6f})"
            )
            print(
                f"   Client: ({self.client_marker.lat:.6f}, {self.client_marker.lon:.6f})"
            )
            print(
                f"   Destination: ({self.destination_marker.lat:.6f}, {self.destination_marker.lon:.6f})"
            )

            return True

        except Exception as e:
            print(f"❌ Erreur carte: {str(e)}")
            import traceback

            traceback.print_exc()

            # Mode fallback simplifié
            self.show_simple_fallback()
            return False

    def check_markers_visibility(self):
        """Vérifier si les marqueurs sont visibles - AVEC DÉLAI"""
        print("🔍 Vérification des marqueurs...")

        if not self.map_view:
            print("   ❌ Pas de carte")
            # Planifier une nouvelle vérification dans 1 seconde
            Clock.schedule_once(lambda dt: self.check_markers_visibility(), 1)
            return

        # Attendre que la carte soit chargée
        if not hasattr(self.map_view, "_zoom") or self.map_view._zoom is None:
            print("   ⏳ Carte en cours de chargement, nouvelle tentative...")
            Clock.schedule_once(lambda dt: self.check_markers_visibility(), 0.5)
            return

        # Maintenant compter les marqueurs
        markers_count = 0
        if hasattr(self.map_view, "_layers"):
            for layer in self.map_view._layers:
                if hasattr(layer, "markers"):
                    markers_count += len(layer.markers)

        print(f"   Marqueurs sur carte: {markers_count}")

        # Vérifier les positions
        if self.driver_marker:
            print(
                f"   Conducteur: ({self.driver_marker.lat:.4f}, {self.driver_marker.lon:.4f})"
            )

        # Si 0 marqueurs, les ajouter manuellement
        if markers_count == 0 and self.driver_marker:
            print("   🔄 Ajout manuel des marqueurs...")
            self.add_markers_manually()

        # Forcer le redessin de la carte
        if hasattr(self.map_view, "do_layout"):
            Clock.schedule_once(lambda dt: self.map_view.do_layout(), 0.1)

    def add_markers_manually(self):
        """Ajouter manuellement les marqueurs si besoin"""
        try:
            # Supprimer d'abord tous les marqueurs existants
            if hasattr(self.map_view, "remove_marker"):
                # Cette méthode n'existe peut-être pas, on fait autrement
                pass

            # Réajouter nos marqueurs
            markers_to_add = []
            if self.driver_marker:
                markers_to_add.append(self.driver_marker)
            if self.client_marker:
                markers_to_add.append(self.client_marker)
            if self.destination_marker:
                markers_to_add.append(self.destination_marker)

            # Les ajouter un par un
            for marker in markers_to_add:
                try:
                    self.map_view.add_marker(marker)
                    print(
                        f"   ✅ Marqueur ajouté: ({marker.lat:.4f}, {marker.lon:.4f})"
                    )
                except:
                    # Alternative: utiliser add_widget
                    self.map_view.add_widget(marker)

            print(f"   ✅ {len(markers_to_add)} marqueurs ajoutés manuellement")

            # Forcer l'actualisation
            if hasattr(self.map_view, "_update_zoom"):
                self.map_view._update_zoom()

        except Exception as e:
            print(f"   ⚠️  Erreur ajout manuel: {e}")

    def show_simple_fallback(self):
        """Afficher une carte simplifiée si OSM échoue"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.graphics import Color, Rectangle, Line

        print("🔄 Activation mode fallback...")

        # Vider le container
        self.map_container.clear_widgets()

        # Créer un widget personnalisé
        class FallbackMap(BoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.orientation = "vertical"
                self.padding = 20

                # Message
                message = Label(
                    text="[b]Carte ZAHEL[/b]\n\nMode navigation simplifié\n\n• [color=0040CC]█[/color] Votre position\n• [color=CC3333]●[/color] Client\n• [color=00AA00]▲[/color] Destination",
                    markup=True,
                    font_size="18sp",
                    halign="center",
                )
                self.add_widget(message)

                # Zone de carte simplifiée
                map_area = BoxLayout(size_hint=(1, 0.6))
                map_area.bind(size=self._update_map)
                map_area.bind(pos=self._update_map)

                # Dessiner la carte
                with map_area.canvas:
                    # Fond (ciel)
                    Color(0.85, 0.90, 1.0, 1)
                    Rectangle(pos=map_area.pos, size=map_area.size)

                    # Route
                    Color(0.5, 0.5, 0.5, 1)
                    road_y = map_area.y + map_area.height * 0.5
                    Line(
                        points=[
                            map_area.x,
                            road_y,
                            map_area.x + map_area.width,
                            road_y,
                        ],
                        width=3,
                    )

                    # Voiture (conducteur)
                    Color(0, 0.4, 0.8, 1)
                    Rectangle(
                        pos=(map_area.x + map_area.width * 0.2 - 10, road_y - 10),
                        size=(20, 20),
                    )

                    # Client
                    Color(0.8, 0.2, 0.2, 1)
                    Rectangle(
                        pos=(map_area.x + map_area.width * 0.5 - 10, road_y - 10),
                        size=(20, 20),
                    )

                    # Destination
                    Color(0, 0.6, 0, 1)
                    Rectangle(
                        pos=(map_area.x + map_area.width * 0.8 - 10, road_y - 10),
                        size=(20, 20),
                    )

                self.add_widget(map_area)

            def _update_map(self, *args):
                self.canvas.clear()
                # Redessiner (logique simplifiée)

        # Ajouter la carte fallback
        fallback = FallbackMap()
        self.map_container.add_widget(fallback)

        print("✅ Mode fallback activé")

    def check_data_saver_mode(self):
        """Vérifier et activer le mode économie de données"""
        # Pour l'instant, simulation
        # Plus tard: lire depuis la configuration ou les préférences utilisateur

        mode_economie = True  # Par défaut activé pour les Comores

        if mode_economie and self.map_view:
            print("🌱 Mode économie de données ACTIVÉ")
            # Désactiver certaines fonctionnalités gourmandes
            self.map_view.double_tap_zoom = False
            self.map_view.touch_zoom = False
            # Limiter le niveau de zoom max
            self.map_view.zoom_max = 16

    def calculate_real_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculer la distance réelle entre deux points GPS (en km)
        Formule de Haversine - précision professionnelle
        """
        import math

        # Rayon de la Terre en km
        R = 6371.0

        # Conversion degrés → radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Différences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Formule de Haversine
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Distance en kilomètres
        distance_km = R * c

        # Arrondir à 1 décimale
        return round(distance_km, 1)

    def calculate_estimated_time(self, distance_km, traffic="normal"):
        """
        Calculer le temps estimé en fonction de la distance
        et du trafic (Comores: circulation modérée)
        """
        # Vitesse moyenne à Moroni (km/h)
        if traffic == "normal":
            speed_kmh = 25  # Circulation normale
        elif traffic == "rush":
            speed_kmh = 15  # Heure de pointe
        else:
            speed_kmh = 30  # Circulation fluide

        # Temps en heures, puis conversion en minutes
        time_hours = distance_km / speed_kmh
        time_minutes = int(time_hours * 60)

        # Ajouter 20% de marge (feux, arrêts, etc.)
        time_minutes = int(time_minutes * 1.2)

        return max(1, time_minutes)  # Minimum 1 minute

    def add_map_markers(self):
        """Ajouter les marqueurs AVEC les icônes personnalisées"""
        from kivy_garden.mapview import MapMarker

        # Chemins vers les icônes
        car_icon = "assets/car_blue.png"
        person_icon = "assets/person_red.png"
        flag_icon = "assets/flag_green.png"

        # Vérifier si les fichiers existent
        import os

        if not os.path.exists(car_icon):
            print("⚠️  Icône voiture non trouvée, utilisation marqueur par défaut")
            car_icon = None

        # Créer les marqueurs
        self.driver_marker = MapMarker(
            lat=self.driver_pos[0],
            lon=self.driver_pos[1],
            source=car_icon if car_icon and os.path.exists(car_icon) else None,
        )

        self.client_marker = MapMarker(
            lat=self.client_pos[0],
            lon=self.client_pos[1],
            source=person_icon if os.path.exists(person_icon) else None,
        )

        self.destination_marker = MapMarker(
            lat=self.dest_pos[0],
            lon=self.dest_pos[1],
            source=flag_icon if os.path.exists(flag_icon) else None,
        )

        # Éviter les warnings
        for marker in [self.driver_marker, self.client_marker, self.destination_marker]:
            if marker:
                marker.allow_stretch = True
                marker.keep_ratio = True

        # Ajouter à la carte
        self.map_view.add_marker(self.driver_marker)
        self.map_view.add_marker(self.client_marker)
        self.map_view.add_marker(self.destination_marker)

        print("✅ Marqueurs avec icônes ajoutés")

    def load_course_data(self):
        """Charger et calculer les vraies données de la course - VERSION AMÉLIORÉE"""
        print("📏 Calcul des données réelles de la course...")

        # 1. Calculer la distance RÉELLE
        distance_to_client = self.calculate_real_distance(
            self.driver_pos[0],
            self.driver_pos[1],
            self.client_pos[0],
            self.client_pos[1],
        )

        distance_client_to_dest = self.calculate_real_distance(
            self.client_pos[0], self.client_pos[1], self.dest_pos[0], self.dest_pos[1]
        )

        total_distance = distance_to_client + distance_client_to_dest

        # 2. Calculer le temps estimé
        total_time = self.calculate_estimated_time(total_distance, traffic="normal")

        # 3. Calculer le prix
        price = self.calculate_price(total_distance)

        # 4. Sauvegarder
        self.course_data = {
            "client": {"name": "Client Test", "phone": "+26934011111"},
            "pickup": {
                "lat": self.client_pos[0],
                "lon": self.client_pos[1],
                "address": "Moroni Centre",
            },
            "destination": {
                "lat": self.dest_pos[0],
                "lon": self.dest_pos[1],
                "address": "Iconi",
            },
            "price": price,
            "distance_km": round(total_distance, 1),
            "distance_to_client": round(distance_to_client, 1),
            "distance_to_dest": round(distance_client_to_dest, 1),
            "estimated_minutes": total_time,
        }

        # 5. Mettre à jour l'interface AVEC PLUS D'INFOS
        if hasattr(self, "distance_label"):
            self.distance_label.text = f"Distance totale: {total_distance:.1f} km"

        if hasattr(self, "time_label"):
            self.time_label.text = f"Temps estimé: {total_time} min | Prix: {price} KMF"

        # 6. Afficher les détails dans les instructions
        if hasattr(self, "instruction_label"):
            self.instruction_label.text = (
                f"Course ZAHEL: {total_distance:.1f} km - {price} KMF"
            )

        print(
            f"✅ Données calculées: {total_distance:.1f} km, {total_time} min, {price} KMF"
        )

    def calculate_price(self, distance_km):
        """Calculer le prix selon la tarification ZAHEL"""
        # Tarif de base
        base_price = 500  # 500 KMF minimum

        # Prix par km (exemple: 300 KMF/km)
        price_per_km = 300

        # Calcul
        price = base_price + (distance_km * price_per_km)

        # Arrondir à la centaine supérieure
        price = ((price + 99) // 100) * 100

        return int(price)

    def start_comores_preloading(self):
        """Démarrer le préchargement des tuiles Comores"""
        print("🌍 Lancement préchargement Comores...")

        try:
            # Importer et démarrer
            from preload_comores_tiles import comores_preloader

            # Démarrer en arrière-plan
            comores_preloader.start_preloading(background=True)

            # Afficher un message
            if hasattr(self, "instruction_label"):
                self.instruction_label.text = "Préchargement cache Comores..."

        except Exception as e:
            print(f"⚠️  Préchargement échoué: {e}")

    def start_interactive_navigation(self, dt):
        """Démarrer la navigation interactive"""
        print("🚦 Navigation interactive démarrée")

        # Attendre 1 seconde que la carte soit complètement chargée
        Clock.schedule_once(lambda dt: self.verify_and_start(), 1)

        # ÉTAPE CRITIQUE : COMMENCER LA COURSE DANS L'API
        if self.commencer_course_api():
            print("✅ Course officiellement commencée, démarrage navigation...")

    def verify_and_start(self):
        """Vérifier puis démarrer"""
        # DEBUG: Vérifier les marqueurs avec délai
        self.check_markers_visibility()

        # Phase 1: Vers le client
        self.status_label.text = "[color=FF9900]● VERS CLIENT[/color]"
        self.instruction_label.text = "Roulez vers le point de prise en charge"
        self.btn_nav.text = "▶ EN COURS..."
        self.btn_nav.background_color = (1, 0.6, 0, 1)

        # Démarrer l'animation APRÈS vérification
        Clock.schedule_once(lambda dt: self.animate_to_client(), 0.5)

    def animate_to_client(self):
        """Animer le déplacement vers le client - VERSION AMÉLIORÉE"""
        print("🎬 Démarrage animation vers client...")

        # Vérifier que les marqueurs existent
        if not self.driver_marker:
            print("⚠️  Marqueur conducteur non trouvé, création...")
            self.driver_marker = MapMarker(
                lat=self.driver_pos[0], lon=self.driver_pos[1]
            )
            if self.map_view:
                self.map_view.add_marker(self.driver_marker)

        # Démarrer l'animation
        import threading

        def animation_thread():
            steps = 30

            for i in range(steps + 1):
                if not hasattr(self, "is_navigating") or not self.is_navigating:
                    break

                progress = i / steps

                # Calculer position INTERPOLÉE
                current_lat = (
                    self.driver_pos[0]
                    + (self.client_pos[0] - self.driver_pos[0]) * progress
                )
                current_lon = (
                    self.driver_pos[1]
                    + (self.client_pos[1] - self.driver_pos[1]) * progress
                )

                # Mettre à jour sur le thread UI
                from kivy.clock import Clock

                Clock.schedule_once(
                    lambda dt, lat=current_lat, lon=current_lon: self.update_marker_position(
                        lat, lon
                    ),
                    0,
                )

                # Mettre à jour la progression
                Clock.schedule_once(
                    lambda dt, p=progress: setattr(self.progress_bar, "value", p * 50),
                    0,
                )

                time.sleep(0.3)  # Vitesse plus lente pour voir l'animation

            # Arrivée chez le client
            if hasattr(self, "is_navigating") and self.is_navigating:
                Clock.schedule_once(lambda dt: self.arrive_at_client(), 0)

        self.is_navigating = True
        thread = threading.Thread(target=animation_thread, daemon=True)
        thread.start()

    def draw_navigation_line(self):
        """Dessiner une ligne d'itinéraire entre les points"""
        try:
            from kivy.graphics import Line, Color

            # Coordonnées des points (converties en pixels)
            points = []

            # Point de départ (conducteur)
            px1, py1 = self.map_view.get_window_xy_from(
                self.driver_pos[0], self.driver_pos[1], self.map_view.zoom
            )

            # Point client
            px2, py2 = self.map_view.get_window_xy_from(
                self.client_pos[0], self.client_pos[1], self.map_view.zoom
            )

            # Point destination
            px3, py3 = self.map_view.get_window_xy_from(
                self.dest_pos[0], self.dest_pos[1], self.map_view.zoom
            )

            # Créer les points pour la ligne
            points = [px1, py1, px2, py2, px3, py3]

            # Dessiner sur la carte
            with self.map_view.canvas.after:
                Color(0, 0.4, 0.8, 0.7)  # Bleu ZAHEL semi-transparent
                Line(points=points, width=3, dash_length=10, dash_offset=5)

            print("🔄 Ligne d'itinéraire dessinée")

        except Exception as e:
            print(f"⚠️  Impossible de dessiner la ligne: {e}")

    def update_marker_position(self, lat, lon):
        """Mettre à jour la position du marqueur conducteur - VERSION SIMPLE"""
        if self.driver_marker:
            # Mettre à jour directement les coordonnées
            self.driver_marker.lat = lat
            self.driver_marker.lon = lon

            # Forcer la mise à jour visuelle
            if hasattr(self.driver_marker, "_trigger_position"):
                self.driver_marker._trigger_position()

            # Recentrer la carte périodiquement
            if self.map_view and hasattr(self, "nav_progress"):
                if self.nav_progress % 0.1 < 0.05:  # Tous les 10% de progression
                    self.map_view.center_on(lat, lon)

    def update_driver_position(self, lat, lon, progress):
        """Mettre à jour la position du conducteur sur la carte"""
        if self.driver_marker and self.map_view:
            # Mettre à jour le marqueur
            self.driver_marker.lat = lat
            self.driver_marker.lon = lon

            # Recentrer légèrement la carte
            if progress < 0.5:
                self.map_view.center_on(lat, lon)

            # Mettre à jour la progression
            self.progress_bar.value = progress * 50  # 0-50% pour phase 1

            # Distance restante
            remaining = self.course_data["distance_km"] * (1 - progress)
            self.distance_label.text = f"Distance: {remaining:.1f} km"

    def arrive_at_client(self):
        """Arrivée chez le client"""
        print("📍 Arrivé chez le client")
        self.status_label.text = "[color=00CC00]● CLIENT CHARGÉ[/color]"
        self.instruction_label.text = "Client pris en charge - Prêt pour destination"
        self.btn_nav.text = "▶ VERS DESTINATION"
        self.btn_nav.background_color = (0, 0.8, 0, 1)

        # Phase 1 terminée
        self.progress_bar.value = 50
        self.current_phase = 1

        # Réactiver le bouton
        self.btn_nav.disabled = False

    def toggle_navigation(self, instance):
        """Gérer le bouton de navigation"""
        if self.current_phase == 0:
            # Déjà en cours vers client
            pass
        elif self.current_phase == 1:
            # Démarrer phase 2: vers destination
            self.start_to_destination()

    def start_to_destination(self):
        """Démarrer vers la destination"""
        print("🚗 Départ vers destination")
        self.status_label.text = "[color=FF9900]● VERS DESTINATION[/color]"
        self.instruction_label.text = "Conduisez vers la destination"
        self.btn_nav.text = "▶ ARRIVÉE..."
        self.btn_nav.background_color = (1, 0.6, 0, 1)
        self.btn_nav.disabled = True

        # Animer vers destination
        self.animate_to_destination()

    def animate_to_destination(self):
        """Animer vers la destination"""
        import threading

        def animation_thread():
            import time

            steps = 40

            for i in range(steps + 1):
                if not self.is_navigating:
                    break

                progress = i / steps
                phase_progress = 0.5 + (progress * 0.5)  # 50% à 100%

                # Position intermédiaire
                current_lat = (
                    self.client_pos[0]
                    + (self.dest_pos[0] - self.client_pos[0]) * progress
                )
                current_lon = (
                    self.client_pos[1]
                    + (self.dest_pos[1] - self.client_pos[1]) * progress
                )

                # Mettre à jour UI
                from kivy.clock import Clock

                Clock.schedule_once(
                    lambda dt, lat=current_lat, lon=current_lon, p=phase_progress: self.update_to_destination(
                        lat, lon, p
                    ),
                    0,
                )

                # Instructions phase 2
                if progress < 0.4:
                    instr = "Prenez la route principale"
                elif progress < 0.8:
                    instr = "Gardez la gauche"
                else:
                    instr = "Destination approche"

                Clock.schedule_once(
                    lambda dt, i=instr: setattr(self.instruction_label, "text", i), 0
                )

                time.sleep(0.5)

            # Arrivée à destination
            if self.is_navigating:
                Clock.schedule_once(lambda dt: self.arrive_at_destination(), 0)

        thread = threading.Thread(target=animation_thread, daemon=True)
        thread.start()

    def update_to_destination(self, lat, lon, progress):
        """Mettre à jour vers destination"""
        if self.driver_marker and self.map_view:
            self.driver_marker.lat = lat
            self.driver_marker.lon = lon

            # Recentrer
            self.map_view.center_on(lat, lon)

            # Progression
            self.progress_bar.value = progress * 100

            # Distance restante (seconde moitié)
            remaining = (
                self.course_data["distance_km"] * 0.5 * (1 - ((progress - 0.5) * 2))
            )
            self.distance_label.text = f"Destination: {remaining:.1f} km"

    def arrive_at_destination(self):
        """Arrivée à destination - VERSION CORRIGÉE"""
        print("🏁 Arrivé à destination")
        self.status_label.text = "[color=00CC00]● DESTINATION ATTEINTE[/color]"
        self.instruction_label.text = "Course terminée avec succès !"
        self.btn_nav.text = "✅ TERMINÉ"
        self.btn_nav.background_color = (0.2, 0.2, 0.2, 1)
        self.btn_nav.disabled = True

        # Progression complète
        self.progress_bar.value = 100

        # ⭐⭐ NOUVEAU CODE CRITIQUE : TERMINER LA COURSE DANS L'API ⭐⭐
        self.terminer_course_dans_api()

        # Retour auto au dashboard après délai
        Clock.schedule_once(lambda dt: self.return_to_dashboard(), 3)

    def terminer_course_dans_api(self):
        """Appeler l'API pour terminer la course officiellement"""
        print("📡 Notification à l'API: course terminée...")

        # Vérifier que la course a bien été commencée
        if not hasattr(self, "course_started") or not self.course_started:
            print("⚠️  ATTENTION: Tentative de terminer une course non commencée!")
            print("   Essayant de commencer la course d'abord...")

            if not self.commencer_course_api():
                print("❌ Échec: impossible de commencer la course")
                return

        try:
            # 1. Récupérer le token conducteur
            from kivy.app import App

            app = App.get_running_app()

            # Essayer différentes sources pour le token
            driver_token = None

            # Source 1: driver_token attribut
            if hasattr(app, "driver_token") and app.driver_token:
                driver_token = app.driver_token
                print(f"   Token source: driver_token attribut")

            # Source 2: immatricule comme token (fallback)
            elif hasattr(app, "immatricule") and app.immatricule:
                driver_token = app.immatricule
                print(f"   Token source: immatricule = {driver_token}")

            # Source 3: chercher dans les écrans
            else:
                # Essayer de récupérer depuis le screen login
                login_screen = (
                    app.root.get_screen("login") if hasattr(app, "root") else None
                )
                if login_screen and hasattr(login_screen, "last_immatricule"):
                    driver_token = login_screen.last_immatricule
                    print(f"   Token source: login screen = {driver_token}")

            if not driver_token:
                print("❌ Aucun token conducteur trouvé!")
                return

            # 2. Récupérer le code de la course
            course_code = getattr(self, "course_code", None)
            if not course_code:
                print("❌ Code course non trouvé")
                return

            print(f"   Course: {course_code}")
            print(f"   Token: {driver_token[:10]}... (longueur: {len(driver_token)})")

            # 3. Appeler l'API
            import requests

            API_BASE_URL = "http://localhost:5001"

            # HEADERS avec le token
            headers = {
                "Authorization": driver_token,
                "Content-Type": "application/json",
            }

            print(f"   URL: {API_BASE_URL}/api/courses/{course_code}/terminer")
            print(f"   Headers: {headers}")

            # 4. Faire la requête avec timeout et logging
            response = requests.post(
                f"{API_BASE_URL}/api/courses/{course_code}/terminer",
                headers=headers,
                timeout=10,
            )

            print(f"   Response status: {response.status_code}")
            print(f"   Response body: {response.text[:200]}")  # Premier 200 caractères

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ Course terminée dans l'API: {result}")

                    # ⭐⭐ CRITIQUE: STOCKER LES INFORMATIONS POUR LE DASHBOARD ⭐⭐
                    from kivy.app import App

                    app = App.get_running_app()

                    # 1. Flag pour forcer le rafraîchissement
                    app.just_completed_course = True

                    # 2. Stocker le gain pour le fallback
                    if "course" in result and "finances" in result["course"]:
                        gain = result["course"]["finances"].get("gain_conducteur", 0)
                        app.last_course_gain = gain
                        print(f"💰 Gain à ajouter: {gain} KMF")

                    # Extraire les gains pour affichage
                    if "course" in result:
                        gain = result["course"].get("gain_conducteur", 0)
                        self.instruction_label.text = (
                            f"✅ Course terminée! Gain: {gain} KMF"
                        )

                    # ⭐ METTRE LE FLAG POUR RAFRAÎCHIR LE DASHBOARD ⭐
                    app.just_completed_course = True

                else:
                    print(f"⚠️  API erreur: {result.get('error')}")
            elif response.status_code == 400:
                print("❌ Erreur 400 - Bad Request")
                print("   Causes possibles:")
                print("   1. Token invalide ou manquant")
                print("   2. Course déjà terminée")
                print("   3. Course pas dans l'état 'en_cours'")
                print("   4. Conducteur pas le propriétaire de la course")
            elif response.status_code == 401:
                print("❌ Erreur 401 - Non autorisé")
                print("   Token d'authentification invalide")
            elif response.status_code == 404:
                print("❌ Erreur 404 - Course non trouvée")
            else:
                print(f"❌ HTTP erreur: {response.status_code}")

        except requests.exceptions.Timeout:
            print("⏰ Timeout API - vérification manuelle nécessaire")
        except Exception as e:
            print(f"❌ Erreur terminaison API: {str(e)}")
            import traceback

            traceback.print_exc()

    def return_to_dashboard(self):
        """Retour au dashboard"""
        print("↪ Retour au dashboard")
        self.manager.current = "dashboard"

    def zoom_map(self, delta):
        """Zoomer/dézoomer la carte"""
        if self.map_view:
            new_zoom = self.map_view.zoom + delta
            if 10 <= new_zoom <= 18:  # Limites de zoom
                self.map_view.zoom = new_zoom
                print(f"🔍 Zoom: {self.map_view.zoom}")

    def center_map(self):
        """Recentrer la carte sur TOUS les points"""
        if self.map_view:
            # Calculer le centre de tous les points
            lats = [self.driver_pos[0], self.client_pos[0], self.dest_pos[0]]
            lons = [self.driver_pos[1], self.client_pos[1], self.dest_pos[1]]

            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)

            # Ajuster le zoom pour voir tous les points
            self.map_view.zoom = 13  # Zoom optimal pour voir les 3 points
            self.map_view.center_on(center_lat, center_lon)

            print(
                f"📍 Carte recentrée sur ({center_lat:.4f}, {center_lon:.4f}) - Zoom: 13"
            )

    def show_debug_info(self):
        """Afficher des informations de debug sur l'écran"""
        debug_text = f"""
        [b]ZAHEL - DEBUG CARTE[/b]
    
        [color=0040CC]● Conducteur:[/color] {self.driver_pos[0]:.6f}, {self.driver_pos[1]:.6f}
        [color=CC3333]● Client:[/color] {self.client_pos[0]:.6f}, {self.client_pos[1]:.6f}
        [color=00AA00]● Destination:[/color] {self.dest_pos[0]:.6f}, {self.dest_pos[1]:.6f}
    
        Distance: {self.calculate_real_distance(*self.driver_pos, *self.client_pos):.2f} km
        """

        # Créer un popup d'info
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label

        popup = Popup(
            title="Debug Carte ZAHEL",
            content=Label(text=debug_text, markup=True),
            size_hint=(0.8, 0.6),
        )
        popup.open()

    def on_leave(self):
        """Nettoyage à la sortie"""
        self.is_navigating = False

    def commencer_course_api(self):
        """Appeler l'API pour commencer la course (changer statut: acceptee → en_cours)"""
        print("🚦 Début de course - Notification à l'API...")

        try:
            from kivy.app import App
            import requests

            app = App.get_running_app()

            # Récupérer le token conducteur
            driver_token = None
            if hasattr(app, "driver_token") and app.driver_token:
                driver_token = app.driver_token
            elif hasattr(app, "immatricule") and app.immatricule:
                driver_token = app.immatricule

            if not driver_token:
                print("❌ Token conducteur non trouvé")
                return False

            # Récupérer le code de la course
            course_code = getattr(self, "course_code", None)
            if not course_code:
                print("❌ Code course non trouvé")
                return False

            print(f"   Course: {course_code}")
            print(f"   Token: {driver_token[:15]}...")

            # Appeler l'API /commencer
            API_BASE_URL = "http://localhost:5001"

            response = requests.post(
                f"{API_BASE_URL}/api/courses/{course_code}/commencer",
                headers={"Authorization": driver_token},
                timeout=10,
            )

            print(f"   API Response: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ Course commencée dans l'API: {result}")
                    self.course_started = True
                    return True
                else:
                    print(f"⚠️  API erreur: {result.get('error')}")
                    return False
            else:
                print(f"❌ HTTP erreur {response.status_code}: {response.text[:100]}")
                return False

        except Exception as e:
            print(f"❌ Erreur début course: {str(e)}")
            return False


# ==================== APPLICATION PRINCIPALE ====================
class SelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(SelectionScreen, self).__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=50, spacing=30)

        # Titre
        title = Label(
            text="[b]ZAHEL[/b]\nVotre transport aux Comores",
            markup=True,
            font_size="24sp",
            halign="center",
            size_hint=(1, 0.3),
        )

        # Sous-titre
        subtitle = Label(
            text="Choisissez votre mode",
            font_size="18sp",
            color=(0.6, 0.6, 0.6, 1),
            halign="center",
            size_hint=(1, 0.1),
        )

        # Bouton Conducteur
        btn_driver = Button(
            text="[size=20][b]CONDUCTEUR[/b][/size]",
            markup=True,
            background_color=(0.2, 0.5, 0.8, 1),
            size_hint=(0.8, None),
            height=80,
            pos_hint={"center_x": 0.5},
        )
        btn_driver.bind(on_press=self.go_to_driver)

        # Bouton Client
        btn_client = Button(
            text="[size=20][b]CLIENT[/b][/size]",
            markup=True,
            background_color=(0.8, 0.3, 0.2, 1),
            size_hint=(0.8, None),
            height=80,
            pos_hint={"center_x": 0.5},
        )
        btn_client.bind(on_press=self.go_to_client)

        # Version
        version = Label(
            text="Version 1.0 • © ZAHEL 2024",
            font_size="12sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, 0.1),
        )

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(btn_driver)
        layout.add_widget(btn_client)
        layout.add_widget(version)

        self.add_widget(layout)

    def go_to_driver(self, instance):
        # Aller à l'écran de login conducteur
        self.manager.current = 'driver_login' 

    def go_to_client(self, instance):
        """Aller à l'écran de connexion client"""
        # Aller à l'écran de login client au lieu de l'accueil direct
        if "client_login" not in self.manager.screen_names:
            self.manager.add_widget(ClientLoginScreen(name="client_login"))
        self.manager.current = "client_login"


class ClientHomeScreen(Screen):
    def __init__(self, **kwargs):
        super(ClientHomeScreen, self).__init__(**kwargs)

        # Layout principal
        main_layout = BoxLayout(orientation="vertical", spacing=10)

        # ========== EN-TÊTE ==========
        header = BoxLayout(size_hint=(1, 0.1), padding=[10, 5, 10, 5])

        # Bouton retour
        btn_back = Button(
            text="←",
            size_hint=(0.1, 1),
            font_size="20sp",
            background_color=(0.2, 0.5, 0.8, 1),
        )
        btn_back.bind(on_press=self.go_back)

        # Titre
        lbl_title = Label(
            text="[b]ZAHEL CLIENT[/b]",
            markup=True,
            font_size="22sp",
            halign="left",
            valign="middle",
            size_hint=(0.8, 1),
        )

        # Bouton compte
        btn_account = Button(text="👤", size_hint=(0.1, 1), font_size="20sp")
        btn_account.bind(on_press=self.show_account)

        header.add_widget(btn_back)
        header.add_widget(lbl_title)
        header.add_widget(btn_account)

        # ========== SECTION RECHERCHE ==========
        search_section = BoxLayout(
            orientation="vertical",
            size_hint=(1, 0.3),
            padding=[20, 10, 20, 10],
            spacing=15,
        )

        # Titre recherche
        lbl_search_title = Label(
            text="[size=18][b]Où allez-vous ?[/b][/size]",
            markup=True,
            halign="left",
            size_hint=(1, 0.3),
        )

        # Champ de recherche
        self.txt_destination = TextInput(
            hint_text="Adresse de destination...",
            multiline=False,
            size_hint=(1, 0.4),
            font_size="16sp",
            padding=[15, 10],
            background_color=(1, 1, 1, 0.9),
        )

        # Bouton "Voir sur la carte"
        btn_show_map = Button(
            text="[size=16]🗺️  Commander sur la carte[/size]", 
            markup=True,
            size_hint=(1, 0.3),
            background_color=(0.2, 0.5, 0.8, 1),
        )
        btn_show_map.bind(on_press=self.show_on_map)

        search_section.add_widget(lbl_search_title)
        search_section.add_widget(self.txt_destination)
        search_section.add_widget(btn_show_map)

        # ========== ADRESSES FRÉQUENTES ==========
        frequent_section = BoxLayout(
            orientation="vertical",
            size_hint=(1, 0.3),
            padding=[20, 0, 20, 10],
            spacing=10,
        )

        lbl_frequent = Label(
            text="[size=16][b]Mes adresses[/b][/size]",
            markup=True,
            halign="left",
            size_hint=(1, 0.3),
        )

        # Conteneur pour les adresses (vide au début)
        self.address_container = GridLayout(cols=2, spacing=10, size_hint=(1, 0.7))
        self.address_container.bind(minimum_height=self.address_container.setter('height'))

        # Bouton pour ajouter une adresse
        btn_add_address = Button(
            text="➕ Ajouter une adresse",
            size_hint=(1, 0.3),
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        btn_add_address.bind(on_press=self.show_add_address_popup)

        frequent_section.add_widget(lbl_frequent)
        frequent_section.add_widget(self.address_container)
        frequent_section.add_widget(btn_add_address)

        # ========== BOUTON COMMANDER ==========
        btn_order = Button(
            text="[size=20][b]COMMANDER UNE COURSE[/b][/size]",
            markup=True,
            size_hint=(1, 0.15),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5},
        )
        btn_order.bind(on_press=self.order_ride)

        # ========== MENU BAS ==========
        bottom_menu = BoxLayout(
            size_hint=(1, 0.08), spacing=20, padding=[20, 5, 20, 10]
        )

        menu_items = [
            ("🏠", "Accueil", self.go_home),
            ("📜", "Mes courses", self.show_history),  # ← "Mes courses" au lieu de "Historique"
            ("👤", "Mon compte", self.show_account),   # ← "Mon compte" au lieu de "Paramètres"
        ]

        for icon, text, callback in menu_items:
            btn = Button(
                text=f"{icon}\n[size=10]{text}[/size]", markup=True, size_hint=(0.25, 1)
            )
            btn.bind(on_press=callback)
            bottom_menu.add_widget(btn)

        # Ajout de tous les widgets au layout principal
        main_layout.add_widget(header)
        main_layout.add_widget(search_section)
        main_layout.add_widget(frequent_section)
        main_layout.add_widget(btn_order)
        main_layout.add_widget(bottom_menu)

        self.add_widget(main_layout)

        # Charger les adresses personnelles
        Clock.schedule_once(lambda dt: self.load_client_adresses(), 1)

    def load_profile(self, dt):
        """Charger le profil du client CONNECTÉ"""
        global api_client
    
        # ✅ Récupérer les données de l'APP (pas de la session)
        app = App.get_running_app()
    
        if hasattr(app, 'client_data') and app.client_data:
            client = app.client_data
            self.lbl_name.text = f"[b]{client.get('nom', 'Client ZAHEL')}[/b]"
            self.lbl_phone.text = f"📱 {client.get('telephone', 'Numéro inconnu')}"
            print(f"👤 Profil chargé: {client.get('nom')} - {client.get('telephone')}")
        else:
            # Fallback sur la session
            print("⚠️ Aucune donnée client dans l'app, vérification session...")
            self.check_session_fallback()
    # ========== MÉTHODES ==========

    def load_client_adresses(self):
        """Charger les adresses fréquentes du client depuis l'API"""
        global api_client
    
        print("🏠 Chargement des adresses personnelles...")
    
        # Vider le conteneur
        self.address_container.clear_widgets()
    
        if api_client is None:
            self.show_default_addresses()
            return
    
        try:
            result = api_client.get_client_adresses()
        
            if result.get('success'):
                adresses = result.get('adresses', [])
            
                if not adresses:
                    self.show_default_addresses()
                    return
            
                print(f"✅ {len(adresses)} adresse(s) personnelle(s) chargée(s)")
            
                # Afficher chaque adresse
                for adresse in adresses:
                    self.add_address_button(adresse)
                
            else:
                print(f"❌ Erreur API adresses: {result.get('error')}")
                self.show_default_addresses()
            
        except Exception as e:
            print(f"❌ Exception chargement adresses: {e}")
            self.show_default_addresses()

    def add_address_button(self, adresse):
        """Ajouter un bouton pour une adresse avec menu contextuel"""
        # Icône selon le type
        icon_map = {
            'personnel': '🏠',
            'travail': '💼', 
            'ecole': '🎓',
            'famille': '👨‍👩‍👧‍👦',
            'autre': '📍'
        }
    
        icon = icon_map.get(adresse.get('type', 'personnel'), '📍')
        nom = adresse.get('nom', 'Adresse')
        texte_adresse = adresse.get('adresse', '')
        adresse_id = adresse.get('id')
    
        # Tronquer l'adresse si trop longue
        if len(texte_adresse) > 30:
            texte_adresse = texte_adresse[:27] + "..."
    
        # Layout principal pour le bouton
        address_widget = BoxLayout(orientation='vertical', 
                                  size_hint=(1, None), 
                                  height=120)
    
        # Bouton principal
        btn_main = Button(
            text=f"{icon}\n[size=14]{nom}[/size]\n[size=12]{texte_adresse}[/size]",
            markup=True,
            halign="center",
            background_color=(0.9, 0.95, 1, 1),
            color=(0, 0, 0, 1),
            size_hint=(1, 0.8)
        )
    
        # Stocker les données
        btn_main.adresse_data = adresse
    
        # Bouton menu (petit)
        btn_menu = Button(
            text="⋯",
            size_hint=(1, 0.2),
            font_size='10sp',
            background_color=(0.8, 0.8, 0.8, 1)
        )
    
        # Bind
        btn_main.bind(on_press=lambda instance: self.select_personal_address(instance.adresse_data))
        btn_menu.bind(on_press=lambda instance: self.show_address_menu(adresse))
    
        address_widget.add_widget(btn_main)
        address_widget.add_widget(btn_menu)
    
        self.address_container.add_widget(address_widget)

    def show_address_menu(self, adresse):
        """Afficher le menu contextuel pour une adresse"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
    
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
    
        lbl_title = Label(text=f"🏠 {adresse.get('nom')}",
                         font_size='18sp',
                         size_hint=(1, 0.3))
    
        lbl_info = Label(text=adresse.get('adresse'),
                        size_hint=(1, 0.4))
    
        # Boutons
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.3))
    
        btn_edit = Button(text='✏️ Modifier')
        btn_delete = Button(text='🗑️ Supprimer',
                           background_color=(0.8, 0.2, 0.2, 1))
        btn_cancel = Button(text='Annuler')
    
        popup = Popup(title='Options adresse',
                     content=content,
                     size_hint=(0.8, 0.5),
                     auto_dismiss=False)
    
        def delete_address(instance):
            popup.dismiss()
            self.confirm_delete_address(adresse)
    
        def edit_address(instance):
            popup.dismiss()
            self.edit_address_popup(adresse)
    
        btn_cancel.bind(on_press=popup.dismiss)
        btn_delete.bind(on_press=delete_address)
        btn_edit.bind(on_press=edit_address)
    
        btn_layout.add_widget(btn_edit)
        btn_layout.add_widget(btn_delete)
        btn_layout.add_widget(btn_cancel)
    
        content.add_widget(lbl_title)
        content.add_widget(lbl_info)
        content.add_widget(btn_layout)
    
        popup.open()

    def confirm_delete_address(self, adresse):
        """Confirmer la suppression d'une adresse"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
    
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
    
        lbl = Label(text=f"Supprimer l'adresse :\n\n"
                        f"[b]{adresse.get('nom')}[/b]\n"
                        f"{adresse.get('adresse')}\n\n"
                        f"Cette action est irréversible.",
                   markup=True,
                   halign='center')
    
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.4))
    
        btn_cancel = Button(text='Annuler')
        btn_confirm = Button(text='🗑️ Supprimer',
                            background_color=(0.8, 0.2, 0.2, 1))
    
        popup = Popup(title='Confirmer suppression',
                     content=content,
                     size_hint=(0.8, 0.5),
                     auto_dismiss=False)
    
        def do_delete(instance):
            popup.dismiss()
            self.delete_address(adresse)
    
        btn_cancel.bind(on_press=popup.dismiss)
        btn_confirm.bind(on_press=do_delete)
    
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_confirm)
    
        content.add_widget(lbl)
        content.add_widget(btn_layout)
    
        popup.open()

    def delete_address(self, adresse):
        """Supprimer l'adresse via l'API"""
        global api_client
    
        print(f"🗑️ Suppression adresse: {adresse.get('id')} - {adresse.get('nom')}")
    
        if api_client and hasattr(api_client, 'delete_client_adresse'):
            result = api_client.delete_client_adresse(adresse.get('id'))
        
            if result.get('success'):
                self.show_info_message(f"✅ Adresse '{adresse.get('nom')}' supprimée")
                # Recharger les adresses
                self.load_client_adresses()
            else:
                self.show_info_message(f"❌ Erreur: {result.get('error')}")
        else:
            self.show_info_message("❌ API non disponible")

    def select_personal_address(self, adresse):
        """Sélectionner une adresse personnelle"""
        adresse_text = adresse.get('adresse', '')
        self.txt_destination.text = adresse_text
    
        print(f"📍 Adresse sélectionnée: {adresse.get('nom')} - {adresse_text}")
    
        # Si on a des coordonnées GPS, on pourrait les stocker pour la carte
        if adresse.get('latitude') and adresse.get('longitude'):
            print(f"📍 Coordonnées: {adresse.get('latitude')}, {adresse.get('longitude')}")

    def show_default_addresses(self):
        """Afficher les adresses par défaut (fallback)"""
        print("⚠️ Affichage adresses par défaut (fallback)")
    
        # Adresses par défaut (les anciennes)
        default_addresses = [
            ("🏠", "Domicile", "Moroni Centre"),
            ("💼", "Travail", "Iconi Business"),
            ("✈️", "Aéroport", "Aéroport Moroni"),
            ("🛒", "Marché", "Marché Volo-volo"),
            ("🏥", "Hôpital", "Hôpital El-Maarouf"),
            ("🎓", "Université", "Université Comores"),
        ]
    
        for icon, name, location in default_addresses:
            btn = Button(
                text=f"{icon}\n[size=14]{name}[/size]\n[size=12]{location}[/size]",
                markup=True,
                halign="center",
                background_color=(0.9, 0.95, 1, 1),
                color=(0, 0, 0, 1)
            )
            btn.bind(on_press=lambda instance, loc=location: self.select_address(loc))
            self.address_container.add_widget(btn)

    def show_add_address_popup(self, instance):
        """Afficher un popup pour ajouter une adresse - VERSION FINALE"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
    
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
    
        # ===== TITRE =====
        lbl_title = Label(
            text='[b]➕ AJOUTER UNE ADRESSE[/b]',
            markup=True,
            font_size='18sp',
            size_hint=(1, 0.12)
        )
    
        # ===== NOM =====
        lbl_nom = Label(
            text='🏷️ Nom de l\'adresse :',
            size_hint=(1, 0.08),
            halign='left'
        )
    
        txt_nom = TextInput(
            hint_text='Ex: Domicile, Travail...',
            multiline=False,
            size_hint=(1, 0.12),
            font_size='16sp'
        )
    
        # ===== ADRESSE + BOUTON =====
        lbl_adresse = Label(
            text='📍 Adresse :',
            size_hint=(1, 0.08),
            halign='left'
        )
    
        address_row = BoxLayout(spacing=10, size_hint=(1, 0.15))
    
        txt_adresse = TextInput(
            hint_text='Rue, quartier, ville...',
            multiline=False,
            size_hint=(0.75, 1),
            font_size='15sp'
        )
    
        btn_locate = Button(
            text='📍',
            size_hint=(0.25, 1),
            font_size='24sp',
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1)
        )
    
        address_row.add_widget(txt_adresse)
        address_row.add_widget(btn_locate)
    
        # ===== TYPE D'ADRESSE =====
        lbl_type = Label(
            text='🏠 Type :',
            size_hint=(1, 0.08),
            halign='left'
        )
    
        types_layout = GridLayout(cols=3, spacing=8, size_hint=(1, 0.18))
    
        types = [
            ('🏠', 'personnel', 'Personnel'),
            ('💼', 'travail', 'Travail'),
            ('🎓', 'ecole', 'École'),
        ]
    
        selected_type = ['personnel']
    
        for icon, value, label in types:
            btn = Button(
                text=f"{icon} {label}",
                font_size='14sp',
                size_hint=(0.32, 1)
            )
        
            def make_callback(val):
                def callback(inst):
                    for child in types_layout.children:
                        if isinstance(child, Button):
                            child.background_color = (0.9, 0.9, 0.9, 1)
                            child.color = (0, 0, 0, 1)
                    inst.background_color = (0.2, 0.6, 0.2, 1)
                    inst.color = (1, 1, 1, 1)
                    selected_type[0] = val
                return callback
        
            btn.bind(on_press=make_callback(value))
            types_layout.add_widget(btn)
    
        # ===== BOUTONS =====
        btn_layout = BoxLayout(spacing=15, size_hint=(1, 0.12))
    
        btn_cancel = Button(
            text='❌ Annuler',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
    
        btn_save = Button(
            text='✅ Enregistrer',
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
    
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_save)
    
        # ===== ASSEMBLAGE =====
        content.add_widget(lbl_title)
        content.add_widget(lbl_nom)
        content.add_widget(txt_nom)
        content.add_widget(lbl_adresse)
        content.add_widget(address_row)
        content.add_widget(lbl_type)
        content.add_widget(types_layout)
        content.add_widget(btn_layout)
    
        # ===== POPUP PRINCIPAL =====
        popup = Popup(
            title='📍 Nouvelle adresse',
            content=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
    
        # ===== FONCTION DE LOCALISATION =====
        def get_current_location(btn_instance):
            """Afficher les positions prédéfinies"""
            print("📍 Bouton localisation cliqué !")
        
            loc_content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
            lbl_loc_title = Label(
                text='[b]📍 CHOISIR UNE POSITION[/b]',
                markup=True,
                font_size='18sp',
                size_hint=(1, 0.15)
            )
        
            grid = GridLayout(cols=2, spacing=10, size_hint=(1, 0.7))
        
            positions = [
                ('🏠 Moroni Centre', -11.6980, 43.2560),
                ('✈️ Aéroport', -11.5330, 43.2670),
                ('🛒 Volo-Volo', -11.7030, 43.2520),
                ('🏥 Hôpital', -11.6910, 43.2610),
            ]
        
            for nom, lat, lon in positions:
                btn = Button(
                    text=nom,
                    size_hint=(1, None),
                    height=70,
                    background_color=(0.9, 0.95, 1, 1)
                )
            
                def make_loc_callback(adr, la, lo):
                    def callback(inst):
                        txt_adresse.text = adr
                        self.current_lat = la
                        self.current_lon = lo
                        loc_popup.dismiss()
                        self.show_info_message(f"✅ Position: {adr}")
                    return callback
            
                btn.bind(on_press=make_loc_callback(nom, lat, lon))
                grid.add_widget(btn)
        
            btn_loc_cancel = Button(
                text='❌ Annuler',
                size_hint=(1, 0.1),
                background_color=(0.8, 0.2, 0.2, 1)
            )
        
            loc_popup = Popup(
                title='📍 Sélectionner une position',
                content=loc_content,
                size_hint=(0.9, 0.7)
            )
        
            btn_loc_cancel.bind(on_press=loc_popup.dismiss)
        
            loc_content.add_widget(lbl_loc_title)
            loc_content.add_widget(grid)
            loc_content.add_widget(btn_loc_cancel)
        
            loc_popup.open()
    
        # ===== BINDINGS =====
        btn_locate.bind(on_press=get_current_location)  # ← ICI C'EST BON
    
        def save_address(instance):
            nom = txt_nom.text.strip()
            adresse = txt_adresse.text.strip()
        
            if not nom:
                self.show_info_message("⚠️ Donnez un nom à l'adresse")
                return
        
            if not adresse:
                self.show_info_message("⚠️ Saisissez une adresse")
                return
        
            print(f"➕ Enregistrement: {nom} - {adresse}")
        
            global api_client
            if api_client:
                result = api_client.add_client_adresse(
                    nom=nom,
                    adresse=adresse,
                    latitude=getattr(self, 'current_lat', None),
                    longitude=getattr(self, 'current_lon', None),
                    type_adresse=selected_type[0]
                )
            
                if result.get('success'):
                    self.show_info_message(f"✅ Adresse '{nom}' enregistrée")
                    popup.dismiss()
                    self.load_client_adresses()
                else:
                    self.show_info_message(f"❌ Erreur: {result.get('error')}")
            else:
                self.show_info_message("❌ API non disponible")
    
        btn_save.bind(on_press=save_address)
        btn_cancel.bind(on_press=popup.dismiss)
    
        popup.open()

    def update_location_fields(self, txt_adresse, btn_locate, adresse, lat, lon):
        """Mettre à jour les champs avec les coordonnées GPS"""
        txt_adresse.text = adresse
        txt_adresse.disabled = False
        btn_locate.text = '📍'
        btn_locate.disabled = False
    
        # Stocker les coordonnées pour l'enregistrement
        self.current_latitude = lat
        self.current_longitude = lon
    
        print(f"✅ Position obtenue: {lat}, {lon}")

    def reset_location_button(self, txt_adresse, btn_locate):
        """Réinitialiser le bouton de localisation"""
        txt_adresse.text = ""
        txt_adresse.disabled = False
        btn_locate.text = '📍'
        btn_locate.disabled = False

    def simulate_location(self, txt_adresse, btn_locate):
        """Simuler une position (fallback)"""
        print("📍 Simulation de position...")
    
        # Position de test (Moroni)
        lat = -11.6980
        lon = 43.2560
    
        # Demander à l'utilisateur
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
    
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        lbl = Label(text="Voulez-vous utiliser votre position actuelle ?\n\n"
                        f"📍 {lat:.6f}, {lon:.6f}\n(Moroni Centre)")
    
        btn_layout = BoxLayout(spacing=10)
        btn_yes = Button(text='✅ Oui', background_color=(0.2, 0.6, 0.2, 1))
        btn_no = Button(text='❌ Non', background_color=(0.8, 0.2, 0.2, 1))
    
        popup = Popup(title='📍 Position actuelle',
                     content=content,
                     size_hint=(0.8, 0.5))
    
        def use_location(instance):
            adresse = f"Position actuelle ({lat:.6f}, {lon:.6f})"
            self.update_location_fields(txt_adresse, btn_locate, adresse, lat, lon)
            popup.dismiss()
    
        btn_yes.bind(on_press=use_location)
        btn_no.bind(on_press=popup.dismiss)
    
        btn_layout.add_widget(btn_yes)
        btn_layout.add_widget(btn_no)
    
        content.add_widget(lbl)
        content.add_widget(btn_layout)
    
        popup.open()

    def go_back(self, instance):
        """Retour à l'écran précédent"""
        # Retour à la connexion client ou sélection selon le cas
        if "client_login" in self.manager.screen_names:
            self.manager.current = "client_login"
        else:
            self.manager.current = "selection"

    def go_home(self, instance):
        """Recharger l'accueil"""
        # Pour l'instant, reste sur la même page
        pass

    def show_account(self, instance):
        """Afficher le compte client (fusionné avec paramètres)"""
        print("👤 Redirection vers compte complet")
        if 'client_account' not in self.manager.screen_names:
            self.manager.add_widget(ClientAccountScreen(name='client_account'))
        self.manager.current = 'client_account'

    def show_on_map(self, instance):
        """Afficher la carte pour sélectionner le trajet"""
        print("🗺️  Affichage de la carte de sélection")
    
        # ⭐⭐ MODIFICATION : Plus besoin d'adresse pour voir la carte !
        # On peut aller à la carte même sans destination
    
        # Option 1 : Si une destination est saisie, la pré-remplir
        destination = self.txt_destination.text.strip()
    
        if destination:
            print(f"📍 Destination saisie: {destination}")
        
            # Essayer de géocoder
            coordinates = self.geocode_local_address(destination)
        
            if coordinates:
                print(f"✅ Adresse trouvée: {coordinates['nom']}")
            
                # Stocker dans l'app pour pré-remplir la carte
                app = App.get_running_app()
                app.selected_destination = {
                    'text': destination,
                    'coordinates': (coordinates['latitude'], coordinates['longitude']),
                    'name': coordinates['nom']
                }
    
        # Aller à la carte (avec ou sans destination)
        self.go_to_map_selection()
    
        print("✅ Redirection vers carte de sélection")

    def logout(self, instance):
        # ✅ AJOUTE AU DÉBUT
        global api_client, API_MODULE_EXISTS

        """Déconnexion client"""
        if api_client:
            api_client.token = None
            api_client.user_type = None

        # Supprimer la session
        try:
            import os

            if os.path.exists("client_session.json"):
                os.remove("client_session.json")
        except:
            pass

        print("✅ Déconnexion réussie")
        self.manager.current = "selection"

    def select_address(self, address):
        """Sélectionner une adresse fréquente"""
        self.txt_destination.text = address
        print(f"Adresse sélectionnée : {address}")

    def order_ride(self, instance):
        """Commander une course - VERSION CORRIGÉE (toujours via carte)"""
        print("\n" + "="*60)
        print("🎯 ORDER_RIDE - TOUJOURS VIA CARTE")
        print("="*60)

        destination_text = self.txt_destination.text.strip()

        if destination_text:
            print(f"🔍 Adresse saisie: '{destination_text}'")
        
            # 1. ESSAYER DE GÉOCODER
            coordinates = self.geocode_local_address(destination_text)
        
            if coordinates:
                print(f"✅ Adresse trouvée: {coordinates['nom']}")
            
                # ⭐⭐ IMPORTANT : TOUJOURS ALLER À LA CARTE MÊME SI ADRESSE VALIDE
                print("🗺️  Adresse valide → Redirection vers carte pour confirmation")
            
                # Stocker la destination pour pré-remplir la carte
                app = App.get_running_app()
                app.selected_destination = {
                    'text': destination_text,
                    'coordinates': (coordinates['latitude'], coordinates['longitude']),
                    'name': coordinates['nom'],
                    'address_found': True  # Flag important !
                }
            
                # Aller à la carte
                self.go_to_map_selection()
            
            else:
                # 2. ADRESSE NON TROUVÉE → Aller à la carte vide
                print(f"❌ Adresse non trouvée → Aller à la carte")
                self.go_to_map_selection()
            
        else:
            # 3. PAS D'ADRESSE → Aller à la carte
            print(f"📱 Pas d'adresse saisie → Aller à la carte")
            self.go_to_map_selection()

    def go_to_order_with_predetermined_destination(self, coordinates, address_text):
        """Aller directement à OrderRideScreen avec une destination pré-définie"""
        print(f"🚀 Destination pré-définie: {address_text}")
        print(f"📍 Coordonnées: {coordinates}")
    
        # Coordonnées de départ par défaut (position actuelle simulée)
        depart_coords = (-11.6980, 43.2560)  # Moroni centre
    
        # Créer l'écran OrderRideScreen avec les deux points
        if 'order_ride' not in self.manager.screen_names:
            self.manager.add_widget(OrderRideScreen(
                name='order_ride',
                depart_coords=depart_coords,
                arrivee_coords=(coordinates['latitude'], coordinates['longitude']),
                destination=f"{coordinates['nom']} ({address_text})"
            ))
        else:
            # Mettre à jour l'écran existant
            existing_screen = self.manager.get_screen('order_ride')
            existing_screen.depart_coords = depart_coords
            existing_screen.arrivee_coords = (coordinates['latitude'], coordinates['longitude'])
            existing_screen.destination = f"{coordinates['nom']} ({address_text})"
    
        # Aller à l'écran de commande
        self.manager.current = 'order_ride'
        print("✅ Redirection vers OrderRideScreen avec destination pré-définie")        

    def geocode_local_address(self, address):
        """Chercher l'adresse dans notre base POI locale - VERSION AMÉLIORÉE"""
        try:
            import sqlite3
            import os
        
            # Chemin vers la base de données
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'zahel_secure.db')
        
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
        
            # NORMALISER la recherche (minuscules, suppression accents)
            search_term = address.lower().strip()
        
            # Recherche AVANCÉE avec plusieurs critères
            cursor.execute('''
                SELECT nom, alias, type, latitude, longitude 
                FROM poi_comores 
                WHERE LOWER(nom) LIKE ? 
                   OR LOWER(alias) LIKE ?
                   OR LOWER(nom) LIKE ?
                   OR LOWER(alias) LIKE ?
                ORDER BY 
                    CASE 
                        WHEN LOWER(nom) = ? THEN 1
                        WHEN LOWER(alias) = ? THEN 2
                        WHEN LOWER(nom) LIKE ? THEN 3
                        WHEN LOWER(alias) LIKE ? THEN 4
                        ELSE 5
                    END
                LIMIT 3
            ''', (
                f'%{search_term}%',  # nom contient
                f'%{search_term}%',  # alias contient
                f'{search_term}%',   # nom commence par
                f'{search_term}%',   # alias commence par
                search_term,         # nom exact
                search_term,         # alias exact
                f'{search_term}%',   # nom commence par (pour tri)
                f'{search_term}%'    # alias commence par (pour tri)
            ))
        
            results = cursor.fetchall()
            conn.close()
        
            if results:
                # Prendre le meilleur résultat
                best_match = results[0]
                return {
                    'nom': best_match[0],
                    'alias': best_match[1],
                    'type': best_match[2],
                    'latitude': best_match[3],
                    'longitude': best_match[4],
                    'source': 'local'
                }
        
            # Si aucun résultat, essayer avec des termes communs
            common_terms = {
                'aéroport': 'Aéroport Prince Said Ibrahim',
                'hopital': 'Hôpital El-Maarouf', 
                'hôpital': 'Hôpital El-Maarouf',
                'marche': 'Marché Volo-volo',
                'marché': 'Marché Volo-volo',
                'université': 'Université des Comores',
                'univ': 'Université des Comores',
                'port': 'Port de Mutsamudu',
                'place': 'Place de France',
                'mosquée': 'Mosquée Vendredi',
                'mosquee': 'Mosquée Vendredi'
            }
        
            for term, poi_name in common_terms.items():
                if term in search_term:
                    # Rechercher ce POI spécifique
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute('SELECT nom, latitude, longitude FROM poi_comores WHERE nom = ?', (poi_name,))
                    result = cursor.fetchone()
                    conn.close()
                
                    if result:
                        return {
                            'nom': result[0],
                            'latitude': result[1],
                            'longitude': result[2],
                            'source': 'local_fallback'
                        }
        
            return None
        except Exception as e:
            print(f"❌ Erreur géocodage local: {e}")
            return None 

    def show_address_not_found_popup(self, address):
        """Afficher un popup quand l'adresse n'est pas trouvée"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
    
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
    
        message = f"L'adresse '{address}' n'a pas été trouvée.\n\n"
        message += "Veuillez utiliser la carte pour sélectionner votre destination."
    
        content.add_widget(Label(
            text=message,
            size_hint=(1, 0.7),
            halign='center'
        ))
    
        buttons = BoxLayout(spacing=10, size_hint=(1, 0.3))
    
        btn_map = Button(text="📍 Utiliser la carte", background_color=(0.2, 0.6, 0.8, 1))
        btn_map.bind(on_press=lambda x: self.go_to_map_selection())
    
        btn_cancel = Button(text="Annuler", background_color=(0.8, 0.2, 0.2, 1))
    
        buttons.add_widget(btn_map)
        buttons.add_widget(btn_cancel)
    
        content.add_widget(buttons)
    
        popup = Popup(
            title='Adresse introuvable',
            content=content,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
    
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()       

    def go_to_map_with_destination(self, coordinates, address_text):
        """Aller à la carte avec une destination pré-remplie"""
        print(f"🗺️  Aller à la carte avec destination: {address_text}")
        print(f"📍 Coordonnées: {coordinates}")
    
        # Stocker la destination pour la carte
        app = App.get_running_app()
        app.selected_destination = {
            'text': address_text,
            'coordinates': (coordinates['latitude'], coordinates['longitude']),
            'name': coordinates['nom']
        }
    
        # Aller à la carte
        if 'map_selection' not in self.manager.screen_names:
            self.manager.add_widget(MapSelectionScreen(name='map_selection'))
    
        self.manager.current = 'map_selection'   

    def show_history(self, instance):
        """Afficher mes courses (historique + en cours)"""
        print("📋 Redirection vers mes courses")
        if 'client_courses' not in self.manager.screen_names:  # ← Changement de nom
            self.manager.add_widget(ClientCoursesScreen(name='client_courses'))  # ← Changement
        self.manager.current = 'client_courses'

    def logout(self, instance):
        # ✅ AJOUTE AU DÉBUT
        global api_client, API_MODULE_EXISTS
        """Déconnexion client"""
        if api_client:
            api_client.token = None
            api_client.user_type = None
    
        # Supprimer la session
        try:
            import os
            if os.path.exists('data/client_session.json'):
                os.remove('data/client_session.json')
                print("✅ Session supprimée")
        except Exception as e:
            print(f"⚠️  Erreur suppression session: {e}")
    
        print("✅ Déconnexion réussie")
        self.manager.current = 'selection'

    def show_info_message(self, message):
        """Afficher un message d'information (version simplifiée)"""
        print(f"ℹ️ {message}")
        # Pour l'instant, juste un print. On peut ajouter un popup plus tard si besoin.    

    def go_to_map_selection(self, instance=None):
        """Aller à l'écran de sélection sur carte"""
        print("🗺️  Redirection vers MapSelectionScreen")
    
        # Vérifier si l'écran existe déjà
        if 'map_selection' not in self.manager.screen_names:
            print("➕ Ajout de MapSelectionScreen...")
            self.manager.add_widget(MapSelectionScreen(name='map_selection'))
    
        # Aller à la carte
        self.manager.current = 'map_selection'
        print("✅ Redirection vers carte effectuée")


class ClientCoursesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
        # Layout principal
        layout = BoxLayout(orientation='vertical')
    
        # En-tête
        header = BoxLayout(size_hint=(1, 0.1))
        btn_back = Button(text='← Retour', size_hint=(0.2, 1))
        btn_back.bind(on_press=self.go_back)
    
        lbl_title = Label(text='📋 Mes courses', 
                         size_hint=(0.6, 1), 
                         font_size='20sp')
    
        btn_refresh = Button(text='🔄', size_hint=(0.1, 1))
        btn_refresh.bind(on_press=lambda x: self.load_history(0))
    
        header.add_widget(btn_back)
        header.add_widget(lbl_title)
        header.add_widget(btn_refresh)

        # ========== ONGLETS ==========
        tabs = BoxLayout(size_hint=(1, 0.06), spacing=2)
    
        btn_all = Button(text='📋 Toutes', size_hint=(0.33, 1))
        btn_all.bind(on_press=lambda x: self.filter_by_status(None))
    
        btn_active = Button(text='🚗 En cours', size_hint=(0.34, 1))
        btn_active.bind(on_press=lambda x: self.show_active_courses())
    
        btn_history = Button(text='📜 Terminées', size_hint=(0.33, 1))
        btn_history.bind(on_press=lambda x: self.filter_by_status('terminee'))
    
        tabs.add_widget(btn_all)
        tabs.add_widget(btn_active)
        tabs.add_widget(btn_history)

        # Filtres
        filter_layout = BoxLayout(size_hint=(1, 0.07), spacing=5, padding=[10, 0, 10, 0])
    
        filters = [
            ('Toutes', None),
            ('🚗 Terminées', 'terminee'),
            ('⏳ En cours', 'en_cours'),
            ('❌ Annulées', 'annulee')
        ]
    
        for text, status in filters:
            btn = Button(text=text, size_hint=(0.25, 1))
            btn.bind(on_press=lambda x, s=status: self.filter_by_status(s))
            filter_layout.add_widget(btn)
        
        # Liste scrollable
        self.scroll_view = ScrollView(size_hint=(1, 0.9))
        self.list_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        
        # Label temporaire
        lbl_loading = Label(text='Chargement de l\'historique...', size_hint_y=None, height=50)
        self.list_layout.add_widget(lbl_loading)
        
        self.scroll_view.add_widget(self.list_layout)
        
        # Ajouter au layout principal
        layout.add_widget(header)
        layout.add_widget(filter_layout)
        layout.add_widget(self.scroll_view)
        
        self.add_widget(layout)

        # Variables pour les filtres
        self.all_courses = []
        self.filtered_courses = []
        
        # Charger les données
        Clock.schedule_once(self.load_history, 0.5)

    def show_active_courses(self):
        """Afficher les courses en cours (pas terminées)"""
        print("🚗 Affichage courses en cours")
    
        if not self.all_courses:
            return
    
        active_statuses = ['en_recherche', 'en_attente', 'acceptee', 'en_cours']
        self.filtered_courses = [c for c in self.all_courses if c.get('statut') in active_statuses]
    
        # Réafficher
        self.list_layout.clear_widgets()
    
        if not self.filtered_courses:
            lbl_empty = Label(text='🚗 Aucune course en cours\n\nCommandez une nouvelle course !',
                             size_hint_y=None,
                             height=120,
                             halign='center')
            self.list_layout.add_widget(lbl_empty)
            return
    
        # Afficher un compteur
        lbl_count = Label(text=f'📊 {len(self.filtered_courses)} course(s) en cours',
                         size_hint_y=None,
                         height=40)
        self.list_layout.add_widget(lbl_count)
    
        for course in self.filtered_courses:
            self.add_course_card(course)

    def filter_by_status(self, status):
        """Filtrer les courses par statut"""
        print(f"🔍 Filtrage par statut: {status}")
    
        if not self.all_courses:
            print("⚠️  Aucune course à filtrer")
            return
    
        if status is None:
            self.filtered_courses = self.all_courses.copy()
        else:
            self.filtered_courses = [c for c in self.all_courses if c.get('statut') == status]
    
        # Réafficher
        self.list_layout.clear_widgets()
    
        if not self.filtered_courses:
            lbl_empty = Label(text=f'📭 Aucune course avec ce statut',
                             size_hint_y=None,
                             height=100)
            self.list_layout.add_widget(lbl_empty)
            return
    
        for course in self.filtered_courses:
            self.add_course_card(course)
    
    def go_back(self, instance):
        self.manager.current = 'client_home'
    
    def load_history(self, dt):
        """Charger l'historique depuis l'API"""
        global api_client
    
        print("=" * 60)
        print("📜 DEBUG load_history - DÉBUT")
    
        try:
            # Vider la liste d'abord
            self.list_layout.clear_widgets()
            self.list_layout.height = 0
        
            print("🗑️  Liste vidée")
        
            # Afficher "Chargement..."
            lbl_loading = Label(text='🔄 Chargement de l\'historique...', 
                               size_hint_y=None, 
                               height=80,
                               font_size='18sp')
            self.list_layout.add_widget(lbl_loading)
            self.list_layout.height += 80
        
            # Forcer la mise à jour
            Clock.schedule_once(lambda dt: self.force_update(), 0.1)
        
            # Vérifier que api_client existe
            if api_client is None:
                self.show_error("API non disponible")
                return
        
            print("📡 Tentative de connexion API pour historique...")
        
            # Appeler l'API
            result = api_client.get_client_courses()
            print(f"📡 Réponse API historique reçue, succès: {result.get('success')}")
        
            # Vider le message de chargement
            self.list_layout.clear_widgets()
        
            if result.get('success'):
                courses = result.get('courses', [])
            
                # STOCKER les courses pour les filtres
                self.all_courses = courses
                self.filtered_courses = courses.copy()
            
                print(f"✅ {len(courses)} course(s) chargée(s) et stockées")
            
                if not courses:
                    lbl_empty = Label(text='📭 Aucune course dans l\'historique\n\nCommandez votre première course !', 
                                     size_hint_y=None, 
                                     height=100,
                                     halign='center')
                    self.list_layout.add_widget(lbl_empty)
                    return
            
                # Afficher chaque course
                display_limit = min(15, len(courses))  # Maximum 15 courses
                for course in courses[:display_limit]:
                    self.add_course_card(course)
                
            else:
                error_msg = result.get('error', 'Erreur inconnue')
                print(f"❌ Erreur API: {error_msg}")
            
                # Afficher erreur + données simulées pour test
                lbl_error = Label(text=f'⚠️ API: {error_msg}\n\nAffichage données de test...', 
                                 size_hint_y=None, 
                                 height=80,
                                 color=(1, 0.5, 0, 1))
                self.list_layout.add_widget(lbl_error)
            
                # Données simulées pour débogage
                self.show_simulated_history()
            
        except Exception as e:
            print(f"❌ Exception dans load_history: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"Exception: {str(e)}")

        # Ajouter un label avec le nombre de courses
        count_label = Label(text=f"📊 {len(courses)} courses trouvées",
                           size_hint_y=None,
                           height=40,
                           font_size='16sp',
                           color=(0.3, 0.3, 0.3, 1))
        self.list_layout.add_widget(count_label)

    def force_update(self):
        """Forcer la mise à jour de l'affichage"""
        self.list_layout.height = self.list_layout.minimum_height
        self.scroll_view.scroll_y = 1  # Remonter en haut

    def test_api_connection(self):
        """Tester la connexion API"""
        global api_client
    
        print("🧪 Test connexion API...")
    
        if api_client is None:
            print("❌ api_client est None")
            return False
    
        try:
            # Test simple
            print(f"🔍 api_client type: {type(api_client)}")
            print(f"🔍 api_client.base_url: {api_client.base_url}")
            print(f"🔍 api_client.token: {api_client.token}")
        
            # Tester avec une requête simple
            import requests
            try:
                response = requests.get(f"{api_client.base_url}/", timeout=5)
                print(f"✅ Test connexion backend: {response.status_code}")
                return response.status_code == 200
            except Exception as e:
                print(f"❌ Test connexion échoué: {e}")
                return False
            
        except Exception as e:
            print(f"❌ Erreur test API: {e}")
            return False
    
    def add_course_card(self, course):
        """Ajouter une carte de course à la liste - VERSION CORRIGÉE"""
    
        print(f"🎯 DEBUG add_course_card reçoit: {course.get('code')}")
    
        # Créer la carte AVEC Canvas pour la couleur de fond
        card = BoxLayout(orientation='vertical', 
                        size_hint_y=None, 
                        height=180,  # Plus grand pour afficher plus d'infos
                        padding=15,
                        spacing=5)
    
        # Ajouter un canvas pour la couleur de fond
        with card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Gris clair
            card.rect = Rectangle(pos=card.pos, size=card.size)
    
        # Lier la position/taille du rectangle à la carte
        card.bind(pos=self.update_card_rect, size=self.update_card_rect)
    
        # ===== LIGNE 1 : Code + Statut =====
        line1 = BoxLayout(size_hint=(1, 0.25), spacing=10)
    
        # Code
        lbl_code = Label(text=f"[b]{course.get('code', 'N/A')}[/b]",
                        markup=True,
                        halign='left',
                        font_size='16sp',
                        size_hint=(0.6, 1),
                        color=(0, 0, 0, 1))
    
        # Statut avec couleur
        statut = course.get('statut', 'inconnu')
        statut_lisible = course.get('statut_lisible', statut)
    
        # Couleurs selon statut
        color_map = {
            'terminee': (0, 0.6, 0, 1),      # Vert
            'en_cours': (0, 0.5, 1, 1),      # Bleu
            'acceptee': (0.2, 0.8, 0.2, 1),  # Vert clair
            'en_recherche': (1, 0.65, 0, 1), # Orange
            'en_attente': (1, 0.8, 0, 1),    # Orange clair
            'annulee': (1, 0.3, 0.3, 1)      # Rouge
        }
    
        status_color = color_map.get(statut, (0.5, 0.5, 0.5, 1))
    
        lbl_status = Label(text=statut_lisible,
                          color=status_color,
                          font_size='14sp',
                          bold=True,
                          size_hint=(0.4, 1))
    
        line1.add_widget(lbl_code)
        line1.add_widget(lbl_status)
    
        # ===== LIGNE 2 : Date et Catégorie =====
        line2 = BoxLayout(size_hint=(1, 0.25), spacing=10)
    
        # Date
        lbl_date = Label(text=f"📅 {course.get('date', 'Date inconnue')}",
                        font_size='14sp',
                        halign='left',
                        size_hint=(0.7, 1),
                        color=(0.3, 0.3, 0.3, 1))
    
        # Catégorie
        categorie = course.get('categorie', 'standard')
        categorie_emoji = {
            'standard': '🚗',
            'confort': '🚙', 
            'luxe': '🏎️',
            'moto': '🏍️'
        }
    
        lbl_cat = Label(text=f"{categorie_emoji.get(categorie, '🚗')} {categorie.upper()}",
                       font_size='13sp',
                       halign='right',
                       size_hint=(0.3, 1),
                       color=(0.4, 0.4, 0.4, 1))
    
        line2.add_widget(lbl_date)
        line2.add_widget(lbl_cat)
    
        # ===== LIGNE 3 : Prix =====
        prix = course.get('prix_convenu', 0)
        prix_final = course.get('prix_final', 0)
    
        if prix_final and prix_final > 0:
            price_text = f"💰 {prix_final} KMF"
        else:
            price_text = f"💰 {prix} KMF"
    
        lbl_price = Label(text=price_text,
                         font_size='18sp',
                         bold=True,
                         size_hint=(1, 0.3),
                         color=(0, 0, 0, 1))
    
        # ===== LIGNE 4 : Conducteur =====
        conducteur = course.get('conducteur')
        if conducteur:
            lbl_driver = Label(text=f"👤 {conducteur.get('nom', 'Inconnu')}",
                              font_size='14sp',
                              size_hint=(1, 0.25),
                              color=(0.2, 0.2, 0.6, 1))
        else:
            lbl_driver = Label(text="👤 Aucun conducteur assigné",
                              font_size='14sp',
                              size_hint=(1, 0.25),
                              color=(0.5, 0.5, 0.5, 1))
    
        # ===== BOUTON DÉTAILS =====
        btn_details = Button(text='📋 Détails',
                           size_hint=(1, 0.35),
                           background_color=(0.2, 0.5, 0.8, 1),
                           color=(1, 1, 1, 1))
        btn_details.bind(on_press=lambda x: self.show_course_details(course))
    
        # Ajouter tous les widgets
        card.add_widget(line1)
        card.add_widget(line2)
        card.add_widget(lbl_price)
        card.add_widget(lbl_driver)
        card.add_widget(btn_details)
    
        # Ajouter à la liste
        self.list_layout.add_widget(card)
        print(f"✅ Carte ajoutée: {course.get('code')}")
    
        return card

    def update_card_rect(self, instance, value):
        """Mettre à jour la position/taille du rectangle de fond"""
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
    
    def show_simulated_history(self):
        """Afficher des données simulées pour test"""
        self.list_layout.clear_widgets()
        
        simulated_courses = [
            {'code': 'ZAHEL-ABC123', 'statut': 'terminee', 'date': '10/02/2024', 'prix': 1500, 'conducteur': {'nom': 'Ahmed'}},
            {'code': 'ZAHEL-DEF456', 'statut': 'annulee', 'date': '09/02/2024', 'prix': 800, 'conducteur': {'nom': 'Mohamed'}},
            {'code': 'ZAHEL-GHI789', 'statut': 'terminee', 'date': '08/02/2024', 'prix': 1200, 'conducteur': {'nom': 'Ali'}},
        ]
        
        for course in simulated_courses:
            self.add_course_card(course)
    
    def show_error(self, message):
        """Afficher un message d'erreur"""
        self.list_layout.clear_widgets()
        lbl_error = Label(text=f"❌ {message}", 
                         size_hint_y=None, 
                         height=100,
                         color=(1, 0, 0, 1))
        self.list_layout.add_widget(lbl_error)
    
    def show_course_details(self, course):
        """Afficher les détails d'une course"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
    
        print(f"📋 Affichage détails pour: {course.get('code')}")
    
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        # Titre
        lbl_title = Label(text=f"[b]📋 Course {course.get('code')}[/b]",
                         markup=True,
                         font_size='20sp',
                         size_hint=(1, 0.2),
                         halign='center')
    
        # Détails
        details = f"""
        [b]Statut:[/b] {course.get('statut_lisible', 'Inconnu')}
        [b]Catégorie:[/b] {course.get('categorie', 'standard').upper()}
        [b]Date:[/b] {course.get('date', 'Date inconnue')}
    
        [b]💰 Prix:[/b] {course.get('prix_convenu', 0)} KMF
        [b]💰 Prix final:[/b] {course.get('prix_final', 0)} KMF
        """
    
        # Conducteur
        conducteur = course.get('conducteur')
        if conducteur:
            details += f"""
        
            [b]👤 Conducteur:[/b]
            • Nom: {conducteur.get('nom', 'Inconnu')}
            • Immatricule: {conducteur.get('immatricule', 'N/A')}
            • Téléphone: {conducteur.get('telephone', 'N/A')}
            """
    
        # Adresses
        depart = course.get('depart', {})
        arrivee = course.get('arrivee', {})
    
        details += f"""
    
        [b]📍 Départ:[/b]
        • {depart.get('adresse', 'Non spécifiée')}
    
        [b]📍 Arrivée:[/b]
        • {arrivee.get('adresse', 'Non spécifiée')}
        """
    
        lbl_details = Label(text=details,
                           markup=True,
                           halign='left',
                           valign='top',
                           size_hint=(1, 0.7),
                           text_size=(400, None))
    
        # Boutons
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.1))
    
        btn_close = Button(text='Fermer', background_color=(0.8, 0.2, 0.2, 1))
        btn_reorder = Button(text='Re-commander', background_color=(0.2, 0.6, 0.2, 1))
    
        # Fermer le popup
        popup = Popup(title='Détails de la course',
                     content=content,
                     size_hint=(0.9, 0.8),
                     auto_dismiss=False)
    
        btn_close.bind(on_press=popup.dismiss)
    
        # OPTION 2 : Ou simplement le retirer du layout
        # btn_layout.remove_widget(btn_reorder)
    
        btn_layout.add_widget(btn_close)
        btn_layout.add_widget(btn_reorder)
    
        content.add_widget(lbl_title)
        content.add_widget(lbl_details)
        content.add_widget(btn_layout)
    
        popup.open()


class ClientAccountScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal
        layout = BoxLayout(orientation='vertical')
        
        # ========== EN-TÊTE ==========
        header = BoxLayout(size_hint=(1, 0.08))
        btn_back = Button(text='← Retour', size_hint=(0.15, 1))
        btn_back.bind(on_press=self.go_back)
        
        lbl_title = Label(text='👤 Mon compte', 
                         size_hint=(0.7, 1), 
                         font_size='20sp')
        
        header.add_widget(btn_back)
        header.add_widget(lbl_title)
        
        # ========== PROFIL CLIENT ==========
        profile_section = BoxLayout(orientation='vertical',
                                   size_hint=(1, 0.3),
                                   padding=[20, 10, 20, 10],
                                   spacing=10)
        
        # Photo/avatar (simulé)
        self.avatar = Label(text='👤',
                           font_size='50sp',
                           size_hint=(1, 0.5),
                           halign='center')
        
        # Nom
        self.lbl_name = Label(text='[b]Client ZAHEL[/b]',
                             markup=True,
                             font_size='18sp',
                             size_hint=(1, 0.2),
                             halign='center')
        
        # Téléphone
        self.lbl_phone = Label(text='📱 +26934011111',
                              font_size='16sp',
                              size_hint=(1, 0.2),
                              halign='center',
                              color=(0.4, 0.4, 0.4, 1))
        
        # Statut
        self.lbl_status = Label(text='✅ Compte actif',
                               font_size='16sp',
                               size_hint=(1, 0.2),
                               halign='center',
                               color=(0, 0.6, 0, 1))
        
        profile_section.add_widget(self.avatar)
        profile_section.add_widget(self.lbl_name)
        profile_section.add_widget(self.lbl_phone)
        profile_section.add_widget(self.lbl_status)
        
        # ========== PARAMÈTRES ==========
        settings_section = BoxLayout(orientation='vertical',
                                    size_hint=(1, 0.4),
                                    padding=[20, 0, 20, 10],
                                    spacing=10)
        
        lbl_settings = Label(text='[size=16][b]Paramètres[/b][/size]',
                            markup=True,
                            halign='left',
                            size_hint=(1, 0.2))

        # 5. Gérer mes adresses
        addr_row = BoxLayout(size_hint=(1, 0.15))
        lbl_addr = Label(text='🏠 Mes adresses',
                        halign='left',
                        size_hint=(0.7, 1))
        btn_addr = Button(text='Gérer',
                         size_hint=(0.3, 0.8),
                         background_color=(0.2, 0.5, 0.8, 1))
        btn_addr.bind(on_press=self.manage_addresses)
        addr_row.add_widget(lbl_addr)
        addr_row.add_widget(btn_addr)                    
        
        # Liste des paramètres
        settings_list = BoxLayout(orientation='vertical',
                                 spacing=5,
                                 size_hint=(1, 0.8))
        
        # 1. Notifications
        notif_row = BoxLayout(size_hint=(1, 0.15))
        lbl_notif = Label(text='🔔 Notifications',
                         halign='left',
                         size_hint=(0.7, 1))
        self.switch_notif = Switch(active=True,
                                  size_hint=(0.3, 1))
        notif_row.add_widget(lbl_notif)
        notif_row.add_widget(self.switch_notif)
        
        # 2. Langue
        lang_row = BoxLayout(size_hint=(1, 0.15))
        lbl_lang = Label(text='🌐 Langue',
                        halign='left',
                        size_hint=(0.7, 1))
        lbl_lang_value = Label(text='Français',
                              halign='right',
                              size_hint=(0.3, 1),
                              color=(0.4, 0.4, 0.4, 1))
        lang_row.add_widget(lbl_lang)
        lang_row.add_widget(lbl_lang_value)
        
        # 3. Confidentialité
        privacy_row = BoxLayout(size_hint=(1, 0.15))
        lbl_privacy = Label(text='🔐 Confidentialité',
                           halign='left',
                           size_hint=(0.7, 1))
        btn_privacy = Button(text='Modifier',
                            size_hint=(0.3, 0.8),
                            background_color=(0.8, 0.8, 0.8, 1))
        privacy_row.add_widget(lbl_privacy)
        privacy_row.add_widget(btn_privacy)
        
        # 4. Changer mot de passe
        pwd_row = BoxLayout(size_hint=(1, 0.15))
        lbl_pwd = Label(text='🔑 Changer mot de passe',
                       halign='left',
                       size_hint=(0.7, 1))
        btn_pwd = Button(text='Modifier', size_hint=(0.3, 0.8), background_color=(0.2, 0.5, 0.8, 1))
        btn_pwd.bind(on_press=self.show_change_password_popup)
        pwd_row.add_widget(lbl_pwd)
        pwd_row.add_widget(btn_pwd)
        
        settings_list.add_widget(notif_row)
        settings_list.add_widget(lang_row)
        settings_list.add_widget(privacy_row)
        settings_list.add_widget(pwd_row)
        settings_list.add_widget(addr_row)
        
        settings_section.add_widget(lbl_settings)
        settings_section.add_widget(settings_list)
        
        # ========== BOUTON DÉCONNEXION ==========
        logout_section = BoxLayout(orientation='vertical',
                                  size_hint=(1, 0.22),
                                  padding=[20, 10, 20, 20])
        
        btn_logout = Button(text='🚪 Déconnexion',
                           size_hint=(1, 0.6),
                           background_color=(0.8, 0.2, 0.2, 1),
                           color=(1, 1, 1, 1))
        btn_logout.bind(on_press=self.logout)
        
        # Version
        lbl_version = Label(text='ZAHEL v1.0 • © 2024',
                           font_size='12sp',
                           size_hint=(1, 0.2),
                           halign='center',
                           color=(0.6, 0.6, 0.6, 1))
        
        logout_section.add_widget(btn_logout)
        logout_section.add_widget(lbl_version)
        
        # ========== ASSEMBLAGE FINAL ==========
        layout.add_widget(header)
        layout.add_widget(profile_section)
        layout.add_widget(settings_section)
        layout.add_widget(logout_section)
        
        self.add_widget(layout)
        
        # Charger les données
        Clock.schedule_once(self.load_profile, 0.5)

    def on_pre_enter(self):
        """Recharger le profil à chaque fois qu'on entre sur l'écran"""
        self.load_profile(None)

    def manage_addresses(self, instance):
        """Ouvrir l'écran de gestion des adresses"""
        print("🏠 Redirection vers écran de gestion des adresses")
    
        # Créer un écran dédié
        if 'manage_addresses' not in self.manager.screen_names:
            self.manager.add_widget(ManageAddressesScreen(name='manage_addresses'))
    
        self.manager.current = 'manage_addresses'

    def show_change_password_popup(self, instance):
        """Afficher le popup pour changer le mot de passe"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
    
        content = BoxLayout(orientation='vertical', spacing=15, padding=25)
    
        # Titre
        lbl_title = Label(
            text='[b]🔑 CHANGER MOT DE PASSE[/b]',
            markup=True,
            font_size='18sp',
            size_hint=(1, 0.2),
            halign='center'
        )
    
        # Ancien mot de passe
        lbl_old = Label(
            text='Ancien mot de passe :',
            size_hint=(1, 0.1),
            halign='left'
        )
    
        txt_old = TextInput(
            password=True,
            hint_text='••••••••',
            multiline=False,
            size_hint=(1, 0.15),
            font_size='16sp'
        )
    
        # Nouveau mot de passe
        lbl_new = Label(
            text='Nouveau mot de passe :',
            size_hint=(1, 0.1),
            halign='left'
        )
    
        txt_new = TextInput(
            password=True,
            hint_text='••••••••',
            multiline=False,
            size_hint=(1, 0.15),
            font_size='16sp'
        )
    
        # Confirmation
        lbl_confirm = Label(
            text='Confirmer le mot de passe :',
            size_hint=(1, 0.1),
            halign='left'
        )
    
        txt_confirm = TextInput(
            password=True,
            hint_text='••••••••',
            multiline=False,
            size_hint=(1, 0.15),
            font_size='16sp'
        )
    
        # Message d'erreur
        lbl_error = Label(
            text='',
            size_hint=(1, 0.1),
            color=(1, 0, 0, 1),
            font_size='12sp'
        )
    
        # Boutons
        btn_layout = BoxLayout(spacing=15, size_hint=(1, 0.2))
    
        btn_cancel = Button(
            text='Annuler',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
    
        btn_save = Button(
            text='Enregistrer',
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
    
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_save)
    
        # Assemblage
        content.add_widget(lbl_title)
        content.add_widget(lbl_old)
        content.add_widget(txt_old)
        content.add_widget(lbl_new)
        content.add_widget(txt_new)
        content.add_widget(lbl_confirm)
        content.add_widget(txt_confirm)
        content.add_widget(lbl_error)
        content.add_widget(btn_layout)
    
        popup = Popup(
            title='🔐 Sécurité',
            content=content,
            size_hint=(0.9, 0.7),
            auto_dismiss=False
        )
    
        def do_change_password(instance):
            old = txt_old.text.strip()
            new = txt_new.text.strip()
            confirm = txt_confirm.text.strip()
        
            # Validation
            if not old or not new or not confirm:
                lbl_error.text = '❌ Tous les champs sont requis'
                return
        
            if new != confirm:
                lbl_error.text = '❌ Les mots de passe ne correspondent pas'
                return
        
            if len(new) < 6:
                lbl_error.text = '❌ Minimum 6 caractères'
                return
        
            # Appel API
            global api_client
            if api_client and hasattr(api_client, 'change_password'):
                result = api_client.change_password(old, new)
            
                if result.get('success'):
                    popup.dismiss()
                    self.show_info_message('✅ Mot de passe modifié avec succès')
                else:
                    error = result.get('error', 'Erreur inconnue')
                    lbl_error.text = f'❌ {error}'
            else:
                lbl_error.text = '❌ API non disponible'
    
        btn_save.bind(on_press=do_change_password)
        btn_cancel.bind(on_press=popup.dismiss)
    
        popup.open()

    def show_info_message(self, message):
        """Afficher un message d'information"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
    
        popup = Popup(
            title='Information',
            content=Label(text=message, halign='center'),
            size_hint=(0.7, 0.3)
        )
        popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'client_home'
    
    def load_profile(self, dt):
        """Charger les données du profil depuis l'application"""
        from kivy.app import App
    
        app = App.get_running_app()
        # ✅ DEBUG : voir ce qu'il y a dans app.client_data
        if hasattr(app, 'client_data'):
            print(f"🔍 app.client_data = {app.client_data}")
        else:
            print("🔍 app.client_data n'existe pas")
        print(f"👤 Chargement du profil...")
    
        # ✅ RÉCUPÉRER LES DONNÉES DU CLIENT CONNECTÉ
        if hasattr(app, 'client_data') and app.client_data:
            client = app.client_data
            nom = client.get('nom', 'Client')
            telephone = client.get('telephone', 'Numéro inconnu')
        
            # Mettre à jour l'affichage
            self.lbl_name.text = f'[b]{nom}[/b]'
            self.lbl_phone.text = f'📱 {telephone}'
            self.lbl_status.text = '✅ Compte actif'
            self.lbl_status.color = (0, 0.6, 0, 1)
        
            print(f"✅ Profil chargé: {nom} - {telephone}")
        else:
            # Fallback (normalement jamais atteint)
            print("⚠️ Aucune donnée client trouvée")
            self.lbl_name.text = '[b]Client ZAHEL[/b]'
            self.lbl_phone.text = '📱 Inconnu'
            self.lbl_status.text = '⚠️ Non connecté'
            self.lbl_status.color = (1, 0.5, 0, 1)
    
    def logout(self, instance):
        """Déconnexion"""
        print("🚪 Déconnexion demandée")
        
        # Confirmation
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        lbl = Label(text='Êtes-vous sûr de vouloir\ndéconnecter votre compte ?',
                   halign='center')
        
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.4))
        
        btn_cancel = Button(text='Annuler')
        btn_confirm = Button(text='Déconnecter',
                           background_color=(0.8, 0.2, 0.2, 1))
        
        popup = Popup(title='Déconnexion',
                     content=content,
                     size_hint=(0.7, 0.4),
                     auto_dismiss=False)
        
        btn_cancel.bind(on_press=popup.dismiss)
        btn_confirm.bind(on_press=lambda x: self.confirm_logout(popup))
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_confirm)
        
        content.add_widget(lbl)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def confirm_logout(self, popup):
        """Confirmer la déconnexion"""
        popup.dismiss()
        
        # Appeler la déconnexion de ClientHomeScreen
        from kivy.app import App
        app = App.get_running_app()
        
        # Rechercher l'instance de ClientHomeScreen
        if 'client_home' in self.manager.screen_names:
            home_screen = self.manager.get_screen('client_home')
            if hasattr(home_screen, 'logout'):
                home_screen.logout(None)
        else:
            # Fallback
            self.manager.current = 'selection'


class ManageAddressesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(size_hint=(1, 0.08))
        btn_back = Button(text='← Retour', size_hint=(0.15, 1))
        btn_back.bind(on_press=self.go_back)
        
        lbl_title = Label(text='🏠 Mes adresses',
                         size_hint=(0.7, 1),
                         font_size='20sp')
        
        btn_add = Button(text='➕', size_hint=(0.15, 1))
        btn_add.bind(on_press=self.show_add_popup)
        
        header.add_widget(btn_back)
        header.add_widget(lbl_title)
        header.add_widget(btn_add)
        
        # Liste
        self.scroll_view = ScrollView(size_hint=(1, 0.92))
        self.list_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        
        self.scroll_view.add_widget(self.list_layout)
        
        layout.add_widget(header)
        layout.add_widget(self.scroll_view)
        
        self.add_widget(layout)
        
        # Charger
        Clock.schedule_once(self.load_addresses, 0.5)
    
    def go_back(self, instance):
        self.manager.current = 'client_account'
    
    def load_addresses(self, dt):
        """Charger les adresses"""
        global api_client
        
        self.list_layout.clear_widgets()
        
        if api_client is None:
            self.show_empty("API non disponible")
            return
        
        result = api_client.get_client_adresses()
        
        if result.get('success'):
            adresses = result.get('adresses', [])
            
            if not adresses:
                self.show_empty("Aucune adresse enregistrée")
                return
            
            for adresse in adresses:
                self.add_address_card(adresse)
        else:
            self.show_error(f"Erreur: {result.get('error')}")
    
    def add_address_card(self, adresse):
        """Ajouter une carte d'adresse"""
        card = BoxLayout(orientation='vertical',
                        size_hint_y=None,
                        height=150,
                        padding=15,
                        spacing=5)
        
        # Fond
        with card.canvas.before:
            Color(0.95, 0.95, 1, 1) if adresse.get('est_principale') else Color(0.98, 0.98, 0.98, 1)
            card.rect = Rectangle(pos=card.pos, size=card.size)
        
        card.bind(pos=self.update_rect, size=self.update_rect)
        
        # En-tête
        header = BoxLayout(size_hint=(1, 0.3))
        
        icon_map = {'personnel': '🏠', 'travail': '💼', 'ecole': '🎓', 'famille': '👨‍👩‍👧‍👦', 'autre': '📍'}
        icon = icon_map.get(adresse.get('type'), '📍')
        
        lbl_name = Label(text=f"{icon} {adresse.get('nom')}",
                        size_hint=(0.7, 1),
                        halign='left',
                        bold=True,
                        font_size='16sp')
        
        if adresse.get('est_principale'):
            lbl_main = Label(text='⭐ Principale',
                           size_hint=(0.3, 1),
                           color=(0.8, 0.5, 0, 1))
            header.add_widget(lbl_main)
        
        header.add_widget(lbl_name)
        
        # Adresse
        lbl_addr = Label(text=adresse.get('adresse'),
                        size_hint=(1, 0.4),
                        halign='left',
                        font_size='14sp')
        
        # Boutons
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.3))
        
        btn_edit = Button(text='Modifier')
        btn_delete = Button(text='Supprimer',
                          background_color=(0.8, 0.2, 0.2, 1))
        
        btn_edit.bind(on_press=lambda x: self.edit_address(adresse))
        btn_delete.bind(on_press=lambda x: self.confirm_delete(adresse))
        
        btn_layout.add_widget(btn_edit)
        btn_layout.add_widget(btn_delete)
        
        card.add_widget(header)
        card.add_widget(lbl_addr)
        card.add_widget(btn_layout)
        
        self.list_layout.add_widget(card)
    
    def update_rect(self, instance, value):
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
    
    def show_add_popup(self, instance):
        # Récupérer ClientHomeScreen pour utiliser sa méthode
        if 'client_home' in self.manager.screen_names:
            home_screen = self.manager.get_screen('client_home')
            if hasattr(home_screen, 'show_add_address_popup'):
                home_screen.show_add_address_popup(instance)
                # Recharger après fermeture du popup
                Clock.schedule_once(self.load_addresses, 1)
    
    def edit_address(self, adresse):
        # À implémenter plus tard
        self.show_info("Édition d'adresse à venir")
    
    def confirm_delete(self, adresse):
        # Similaire à la méthode dans ClientHomeScreen
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        lbl = Label(text=f"Supprimer : {adresse.get('nom')} ?")
        
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.4))
        btn_cancel = Button(text='Annuler')
        btn_confirm = Button(text='Supprimer',
                           background_color=(0.8, 0.2, 0.2, 1))
        
        popup = Popup(title='Confirmer',
                     content=content,
                     size_hint=(0.7, 0.4))
        
        def do_delete(instance):
            popup.dismiss()
            self.delete_address(adresse)
        
        btn_cancel.bind(on_press=popup.dismiss)
        btn_confirm.bind(on_press=do_delete)
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_confirm)
        
        content.add_widget(lbl)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def delete_address(self, adresse):
        global api_client
        
        if api_client and hasattr(api_client, 'delete_client_adresse'):
            result = api_client.delete_client_adresse(adresse.get('id'))
            
            if result.get('success'):
                self.show_info(f"✅ {adresse.get('nom')} supprimée")
                self.load_addresses(0)
            else:
                self.show_error(f"❌ {result.get('error')}")
    
    def show_empty(self, message):
        lbl = Label(text=message,
                   size_hint_y=None,
                   height=100)
        self.list_layout.add_widget(lbl)
    
    def show_error(self, message):
        lbl = Label(text=f"❌ {message}",
                   size_hint_y=None,
                   height=100,
                   color=(1, 0, 0, 1))
        self.list_layout.add_widget(lbl)
    
    def show_info(self, message):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        
        popup = Popup(title='Information',
                     content=Label(text=message),
                     size_hint=(0.7, 0.3))
        popup.open()


class MapSelectionScreen(Screen):
    """Écran pour sélectionner départ/arrivée sur la carte"""
    def __init__(self, **kwargs):
        super(MapSelectionScreen, self).__init__(**kwargs)
        
        self.depart_coords = None  # (lat, lng)
        self.arrivee_coords = None  # (lat, lng)
        self.mode_selection = "depart"  # "depart" ou "arrivee"
        self.map_view = None
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        # ========== EN-TÊTE ==========
        header = BoxLayout(size_hint=(1, 0.08), padding=[10, 5, 10, 5])
        
        btn_back = Button(
            text='←',
            size_hint=(0.1, 1),
            font_size='20sp'
        )
        btn_back.bind(on_press=self.go_back)
        
        self.lbl_title = Label(
            text='[b]📍 Sélectionnez votre point de départ[/b]',
            markup=True,
            font_size='18sp',
            halign='center'
        )
        
        header.add_widget(btn_back)
        header.add_widget(self.lbl_title)
        
        # ========== INSTRUCTIONS ==========
        instructions_box = BoxLayout(
            orientation='vertical', 
            size_hint=(1, 0.1), 
            padding=[20, 5],
            spacing=5
        )
        
        self.lbl_instructions = Label(
            text='[size=16][color=2E7D32]📌 Sélectionnez votre point de départ sur la carte[/color][/size]',
            markup=True,
            halign='center'
        )
        
        self.lbl_coords = Label(
            text='Latitude: --, Longitude: --',
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='center'
        )
        
        instructions_box.add_widget(self.lbl_instructions)
        instructions_box.add_widget(self.lbl_coords)
        
        # ========== CONTAINER POUR LA CARTE ==========
        self.map_container = BoxLayout(size_hint=(1, 0.7))
        
        # ========== BOUTONS DE CONTRÔLE ==========
        controls_box = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.12),
            padding=[20, 10, 20, 10],
            spacing=10
        )
        
        # Bouton pour passer à l'arrivée
        self.btn_next = Button(
            text='[size=16]📌 Valider départ[/size]',
            markup=True,
            size_hint=(0.5, 1),
            background_color=(0.2, 0.5, 0.8, 1),
            disabled=True
        )
        self.btn_next.bind(on_press=self.next_step)
        
        # Bouton pour annuler la sélection
        btn_reset = Button(
            text='[size=16]↺ Effacer[/size]',
            markup=True,
            size_hint=(0.25, 1),
            background_color=(0.8, 0.5, 0.2, 1)
        )
        btn_reset.bind(on_press=self.reset_selection)
        
        # Bouton pour utiliser ma position
        btn_my_location = Button(
            text='[size=16]📍 Ma position[/size]',
            markup=True,
            size_hint=(0.25, 1),
            background_color=(0.2, 0.6, 0.2, 1)
        )
        btn_my_location.bind(on_press=self.use_my_location)
        
        controls_box.add_widget(btn_reset)
        controls_box.add_widget(btn_my_location)
        controls_box.add_widget(self.btn_next)
        
        # ========== ÉTAPES ==========
        steps_box = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.05),
            padding=[20, 0]
        )
        
        self.step_depart = Label(
            text='[size=14][b]1. Départ[/b][/size]',
            markup=True,
            color=(0.2, 0.5, 0.8, 1)
        )
        
        self.step_arrivee = Label(
            text='[size=14]2. Arrivée[/size]',
            markup=True,
            color=(0.5, 0.5, 0.5, 1)
        )
        
        self.step_confirm = Label(
            text='[size=14]3. Confirmation[/size]',
            markup=True,
            color=(0.5, 0.5, 0.5, 1)
        )
        
        steps_box.add_widget(self.step_depart)
        steps_box.add_widget(Label(text='→', size_hint=(0.1, 1)))
        steps_box.add_widget(self.step_arrivee)
        steps_box.add_widget(Label(text='→', size_hint=(0.1, 1)))
        steps_box.add_widget(self.step_confirm)
        
        # ========== ASSEMBLAGE ==========
        main_layout.add_widget(header)
        main_layout.add_widget(instructions_box)
        main_layout.add_widget(self.map_container)
        main_layout.add_widget(controls_box)
        main_layout.add_widget(steps_box)
        
        self.add_widget(main_layout)
        
        # Initialiser la carte après un court délai
        from kivy.clock import Clock
        Clock.schedule_once(self.init_map, 0.1)
    
    def init_map(self, dt):
        """Initialiser la carte OpenStreetMap"""
        try:
            from kivy_garden.mapview import MapView
            import os
            
            print("🗺️  Initialisation carte pour sélection...")
            
            # Créer la carte centrée sur Moroni
            self.map_view = MapView(
                zoom=14,
                lat=-11.6980,  # Moroni centre
                lon=43.2560,
                size_hint=(1, 1),
                cache_dir=os.path.join(os.getcwd(), "cache", "osm_tiles_comores"),
                double_tap_zoom=True,
            )
            
            # Lier le clic sur la carte
            self.map_view.bind(on_touch_down=self.on_map_touch)
            
            # Ajouter la carte au container
            self.map_container.add_widget(self.map_view)
            
            print("✅ Carte initialisée pour sélection")
            
        except Exception as e:
            print(f"❌ Erreur initialisation carte: {e}")
            self.show_fallback_map()

    def on_enter(self):
        """Quand l'écran de carte devient actif - VERSION AMÉLIORÉE"""
        super(MapSelectionScreen, self).on_enter()
    
        # Vérifier si une destination a été présélectionnée
        app = App.get_running_app()
    
        if hasattr(app, 'selected_destination') and app.selected_destination:
            destination = app.selected_destination
            print(f"🎯 Destination présélectionnée: {destination['text']}")
        
            # ⭐⭐ NOUVEAU : VÉRIFIER SI ADRESSE TROUVÉE
            if destination.get('address_found'):
                print(f"📍 Adresse valide trouvée → Mode confirmation départ seulement")
            
                # 1. Centrer la carte sur la destination
                self.center_on_destination(destination['coordinates'])
            
                # 2. Ajouter un marqueur d'arrivée
                self.add_destination_marker(destination['coordinates'], destination['text'])
            
                # 3. RÉINITIALISER LE FLUX POUR CONFIRMER DÉPART SEULEMENT
                self.mode_selection = "depart"  # Retour au départ
                self.lbl_title.text = '[b]📍 Confirmez votre point de départ[/b]'
                self.lbl_instructions.text = '[size=16][color=2E7D32]Votre destination est déjà sélectionnée. Choisissez votre point de départ.[/color][/size]'
            
                # 4. METTRE LES COORDONNÉES D'ARRIVÉE DIRECTEMENT
                self.arrivee_coords = destination['coordinates']
            
                # 5. MODIFIER LES ÉTAPES VISUELLES
                self.step_depart.color = (0.2, 0.5, 0.8, 1)  # Départ en bleu
                self.step_arrivee.color = (0, 0.6, 0, 1)     # Arrivée en vert (déjà fait)
                self.step_arrivee.text = '[size=14][b]2. Arrivée (✓)[/b][/size]'
            
                print(f"ℹ️ Destination pré-sélectionnée: {destination['name']}")
            
                # Nettoyer après utilisation
                delattr(app, 'selected_destination')
            else:
                # Ancien comportement pour carte normale
                self.center_on_destination(destination['coordinates'])
                self.add_destination_marker(destination['coordinates'], destination['text'])
                print(f"ℹ️ Destination: {destination['name']}")
                delattr(app, 'selected_destination')
        else:
            print("📍 Pas de destination présélectionnée → carte normale")
            if hasattr(self, 'map_view') and self.map_view:
                self.map_view.center_on(-11.698, 43.256)
                self.map_view.zoom = 14
    
    def on_map_touch(self, instance, touch):
        """Gérer le clic sur la carte"""
        if self.map_view.collide_point(*touch.pos) and touch.is_double_tap:
            # Obtenir les coordonnées du point cliqué
            lat, lon = self.map_view.get_latlon_at(touch.x, touch.y, self.map_view.zoom)
            
            print(f"📍 Clic sur carte: ({lat:.6f}, {lon:.6f})")
            
            # Stocker les coordonnées selon le mode
            if self.mode_selection == "depart":
                self.depart_coords = (lat, lon)
                self.lbl_coords.text = f'Départ: {lat:.6f}, {lon:.6f}'
                
                # Ajouter un marqueur sur la carte
                self.add_marker(lat, lon, "depart")
                
                # Activer le bouton suivant
                self.btn_next.disabled = False
                
            elif self.mode_selection == "arrivee":
                self.arrivee_coords = (lat, lon)
                self.lbl_coords.text = f'Arrivée: {lat:.6f}, {lon:.6f}'
                
                # Ajouter un marqueur sur la carte
                self.add_marker(lat, lon, "arrivee")
                
                # Activer le bouton suivant
                self.btn_next.disabled = False
            
            return True
        return False
    
    def add_marker(self, lat, lon, marker_type):
        """Ajouter un marqueur sur la carte - VERSION CORRIGÉE (1 seul par type)"""
        try:
            from kivy_garden.mapview import MapMarker
            import os
        
            # 1. SUPPRIMER L'ANCIEN MARQUEUR DU MÊME TYPE
            if marker_type == "depart" and hasattr(self, 'depart_marker') and self.depart_marker:
                self.map_view.remove_marker(self.depart_marker)
                print(f"🗑️  Ancien marqueur départ supprimé")
        
            elif marker_type == "arrivee" and hasattr(self, 'arrivee_marker') and self.arrivee_marker:
                self.map_view.remove_marker(self.arrivee_marker)
                print(f"🗑️  Ancien marqueur arrivée supprimé")
        
            # 2. CRÉER LE NOUVEAU MARQUEUR
            marker = MapMarker(lat=lat, lon=lon)
        
            # Charger l'icône appropriée
            if marker_type == "depart":
                icon_path = os.path.join("assets", "person_red.png")
                marker.size = (40, 40)
                self.depart_marker = marker  # Stocker la référence
            else:  # arrivee
                icon_path = os.path.join("assets", "flag_green.png")
                marker.size = (40, 40)
                self.arrivee_marker = marker  # Stocker la référence
        
            if os.path.exists(icon_path):
                marker.source = icon_path
            else:
                print(f"⚠️  Icône non trouvée: {icon_path}")
        
            # 3. AJOUTER LE MARQUEUR À LA CARTE
            self.map_view.add_marker(marker)
        
            # 4. CENTRER LA CARTE SUR LE MARQUEUR
            self.map_view.center_on(lat, lon)
            self.map_view.zoom = 16  # Zoom rapproché
        
            print(f"✅ Marqueur {marker_type} ajouté: ({lat:.6f}, {lon:.6f})")
        
        except Exception as e:
            print(f"⚠️  Erreur ajout marqueur: {e}")
    
    def next_step(self, instance):
        """Passer à l'étape suivante - VERSION ADAPTÉE"""
        if self.mode_selection == "depart":
        
            # ⭐⭐ NOUVEAU : VÉRIFIER SI ARRIVÉE EST DÉJÀ PRÉ-SÉLECTIONNÉE
            if hasattr(self, 'arrivee_coords') and self.arrivee_coords is not None:
                print("✅ Arrivée déjà pré-sélectionnée → Passer directement à la confirmation")
                self.confirm_selection()
            else:
                # Comportement normal
                self.mode_selection = "arrivee"
                self.lbl_title.text = '[b]📍 Sélectionnez votre point d\'arrivée[/b]'
                self.lbl_instructions.text = '[size=16][color=2E7D32]Appuyez sur la carte pour choisir le point d\'arrivée[/color][/size]'
                self.btn_next.text = '[size=16]✅ Confirmer trajet[/size]'
            
                # Mettre à jour les étapes visuelles
                self.step_depart.color = (0.5, 0.5, 0.5, 1)
                self.step_arrivee.color = (0.2, 0.5, 0.8, 1)
            
                # Désactiver le bouton jusqu'à la sélection
                self.btn_next.disabled = True
                self.lbl_coords.text = 'Latitude: --, Longitude: --'
    
        elif self.mode_selection == "arrivee":
            # Les deux points sont sélectionnés, passer à l'écran de commande
            self.confirm_selection()
    
    def confirm_selection(self):
        """Confirmer la sélection et aller à l'écran de commande"""
        if self.depart_coords and self.arrivee_coords:
            print(f"✅ Trajet sélectionné:")
            print(f"   Départ: {self.depart_coords}")
            print(f"   Arrivée: {self.arrivee_coords}")
            
            # Créer l'écran OrderRideScreen avec les coordonnées
            order_screen = OrderRideScreen(
                name='order_ride',
                depart_coords=self.depart_coords,
                arrivee_coords=self.arrivee_coords,
                destination="Destination sélectionnée sur carte"
            )
            
            # Ajouter l'écran s'il n'existe pas
            if 'order_ride' not in self.manager.screen_names:
                self.manager.add_widget(order_screen)
            else:
                # Mettre à jour l'écran existant
                existing_screen = self.manager.get_screen('order_ride')
                existing_screen.depart_coords = self.depart_coords
                existing_screen.arrivee_coords = self.arrivee_coords
            
            # Aller à l'écran de commande
            self.manager.current = 'order_ride'
        else:
            print("❌ Sélection incomplète")
    
    def use_my_location(self, instance):
        """Utiliser la position actuelle (simulée pour l'instant)"""
        print("📍 Utilisation de la position actuelle (simulée)")
    
        # Pour l'instant, simulation : position fixe à Moroni
        simulated_location = (-11.6980, 43.2560)  # Moroni Centre
    
        if self.mode_selection == "depart":
            self.depart_coords = simulated_location
            self.lbl_coords.text = f'Départ: {simulated_location[0]:.6f}, {simulated_location[1]:.6f}'
            self.add_marker(simulated_location[0], simulated_location[1], "depart")
        else:
            self.arrivee_coords = simulated_location
            self.lbl_coords.text = f'Arrivée: {simulated_location[0]:.6f}, {simulated_location[1]:.6f}'
            self.add_marker(simulated_location[0], simulated_location[1], "arrivee")
    
        self.btn_next.disabled = False
        self.map_view.center_on(simulated_location[0], simulated_location[1])
    
    def reset_selection(self, instance):
        """Effacer la sélection courante"""
        if self.mode_selection == "depart":
            self.depart_coords = None
            if hasattr(self, 'depart_marker') and self.depart_marker:
                self.map_view.remove_marker(self.depart_marker)
                self.depart_marker = None
            self.lbl_coords.text = 'Latitude: --, Longitude: --'
            self.btn_next.disabled = True
            print("↺ Départ effacé")
        else:
            self.arrivee_coords = None
            if hasattr(self, 'arrivee_marker') and self.arrivee_marker:
                self.map_view.remove_marker(self.arrivee_marker)
                self.arrivee_marker = None
            self.lbl_coords.text = 'Latitude: --, Longitude: --'
            self.btn_next.disabled = True
            print("↺ Arrivée effacée")
    
    def show_fallback_map(self):
        """Afficher une carte de secours"""
        from kivy.uix.label import Label
        from kivy.graphics import Color, Rectangle
        
        fallback = BoxLayout(orientation='vertical', padding=20)
        
        message = Label(
            text='[size=18][b]Carte ZAHEL[/b][/size]\n\n'
                 'Pour sélectionner votre trajet:\n\n'
                 '1. Départ: Position actuelle\n'
                 '2. Arrivée: Sera demandée après\n\n'
                 'Mode sélection simplifié',
            markup=True,
            halign='center'
        )
        
        fallback.add_widget(message)
        self.map_container.add_widget(fallback)
    
    def go_back(self, instance):
        """Retour à l'écran précédent"""
        self.manager.current = 'client_home'
    
    def on_leave(self):
        """Nettoyage à la sortie"""
        # Réinitialiser pour la prochaine utilisation
        self.depart_coords = None
        self.arrivee_coords = None
        self.mode_selection = "depart"
        
        # Réinitialiser l'interface
        self.lbl_title.text = '[b]📍 Sélectionnez votre point de départ[/b]'
        self.lbl_instructions.text = '[size=16][color=2E7D32]Appuyez sur la carte pour choisir le point de départ[/color][/size]'
        self.btn_next.text = '[size=16]📌 Valider départ[/size]'
        self.btn_next.disabled = True
        self.lbl_coords.text = 'Latitude: --, Longitude: --'
        
        # Réinitialiser les étapes visuelles
        self.step_depart.color = (0.2, 0.5, 0.8, 1)
        self.step_arrivee.color = (0.5, 0.5, 0.5, 1)
        self.step_confirm.color = (0.5, 0.5, 0.5, 1)

    def center_on_destination(self, coordinates):
        """Centrer la carte sur les coordonnées données"""
        print(f"🎯 Centrage carte sur: {coordinates}")
    
        try:
            # CORRECTION: utiliser self.map_view (pas self.mapview)
            if hasattr(self, 'map_view') and self.map_view:
                lat, lon = coordinates
                self.map_view.center_on(lat, lon)
                self.map_view.zoom = 16  # Zoom approprié
                print(f"✅ Carte centrée sur ({lat}, {lon})")
            else:
                print("⚠️ MapView non trouvée")
        except Exception as e:
            print(f"❌ Erreur centrage carte: {e}")

    def add_destination_marker(self, coordinates, text):
        """Ajouter un marqueur de destination sur la carte"""
        try:
            from kivy_garden.mapview import MapMarker
        
            lat, lon = coordinates
        
            # Créer le marqueur
            marker = MapMarker(
                lat=lat, 
                lon=lon,
                source='assets/flag_green.png'  # Utilise ton icône existante
            )
        
            # CORRECTION: utiliser self.map_view (pas self.mapview)
            if hasattr(self, 'map_view') and self.map_view:
                self.map_view.add_marker(marker)
                print(f"📍 Marqueur ajouté: {text} à ({lat}, {lon})")
            
                # Stocker pour référence
                if not hasattr(self, 'destination_markers'):
                    self.destination_markers = []
                self.destination_markers.append(marker)
        except Exception as e:
            print(f"❌ Erreur ajout marqueur: {e}")


class OrderRideScreen(Screen):
    def __init__(self, depart_coords=None, arrivee_coords=None, destination="", **kwargs):
        super(OrderRideScreen, self).__init__(**kwargs)
    
        # ⭐⭐ AJOUTER DES VALEURS PAR DÉFAUT SI NONE
        self.depart_coords = depart_coords or (-11.6980, 43.2560)
        self.arrivee_coords = arrivee_coords or (-11.7100, 43.2650)
        self.destination = destination

        # ⭐⭐ OPTIMISATION : Si destination est longue, l'indiquer clairement
        if len(destination) > 30:
            self.destination_display = destination[:30] + "..."
        else:
            self.destination_display = destination

        # Layout principal avec défilement
        from kivy.uix.scrollview import ScrollView

        scroll = ScrollView(size_hint=(1, 1))
        main_layout = BoxLayout(
            orientation="vertical",
            spacing=15,
            padding=[20, 20, 20, 30],
            size_hint_y=None,
        )
        main_layout.bind(minimum_height=main_layout.setter("height"))

        # ========== EN-TÊTE ==========
        header = BoxLayout(size_hint=(1, None), height=60)

        btn_back = Button(
            text="←",
            size_hint=(0.15, 1),
            font_size="24sp",
            background_color=(0.2, 0.5, 0.8, 1),
        )
        btn_back.bind(on_press=self.go_back)

        lbl_title = Label(
            text="[b]Commander une course[/b]",
            markup=True,
            font_size="20sp",
            halign="center",
        )

        header.add_widget(btn_back)
        header.add_widget(lbl_title)

        # ========== DESTINATION ==========
        dest_box = BoxLayout(
            orientation="vertical", size_hint=(1, None), height=100, spacing=10
        )

        lbl_dest_title = Label(
            text="[size=16][b]Votre itinéraire[/b][/size]",
            markup=True,
            halign="left",
            size_hint=(1, 0.4),
        )

        # Adresse de départ (position actuelle simulée)
        self.txt_from = TextInput(
            text="📍 Position actuelle",
            multiline=False,
            readonly=True,
            size_hint=(1, 0.3),
            background_color=(0.9, 0.95, 1, 1),
            font_size="14sp",
        )

        # Adresse d'arrivée
        self.txt_to = TextInput(
            text=self.destination_display, 
            multiline=False,
            readonly=True,
            size_hint=(1, 0.3),
            background_color=(0.9, 0.95, 1, 1),
            font_size="14sp",
        )

        dest_box.add_widget(lbl_dest_title)
        dest_box.add_widget(self.txt_from)
        dest_box.add_widget(self.txt_to)

        # ========== CHOIX DU SERVICE ==========
        service_box = BoxLayout(
            orientation="vertical", size_hint=(1, None), height=300, spacing=15
        )

        lbl_service = Label(
            text="[size=16][b]Choisissez votre service[/b][/size]",
            markup=True,
            halign="left",
            size_hint=(1, 0.2),
        )

        # Conteneur pour les options de service
        services_container = GridLayout(cols=1, spacing=15, size_hint=(1, 0.8))

        # Options de service - AVEC PRIX CALCULÉS
        def calculate_service_price(service_id, distance_km):
            """Calculer le prix pour un service donné"""
            # TARIFICATION PAR CATÉGORIE (KMF)
            tarifs_base = {
                'standard': 500,
                'confort': 600,
                'luxe': 750,
                'moto': 300
            }
    
            tarifs_km = {
                'standard': 300,
                'confort': 360,
                'luxe': 450,
                'moto': 180
            }
    
            if service_id in tarifs_base:
                base = tarifs_base[service_id]
                tarif_km = tarifs_km[service_id]
                price = base + (distance_km * tarif_km)
                # Arrondir à la centaine supérieure
                price = ((price + 99) // 100) * 100
                return price
            return 0

        # Calculer la distance (simplifié pour l'instant)
        distance_km = 4.2

        self.services = [
            {
                "id": "standard",
                "name": "Course Standard",
                "icon": "🚗",
                "price": f"{calculate_service_price('standard', distance_km):,} KMF",
                "desc": "Prix recommandé • Voiture économique",
                "color": (0.2, 0.6, 0.2, 1),
                "real_price": calculate_service_price('standard', distance_km)
            },
            {
                "id": "confort",
                "name": "Confort",
                "icon": "✨",
                "price": f"{calculate_service_price('confort', distance_km):,} KMF",
                "desc": "Voitures récentes • Confort assuré",
                "color": (0.8, 0.5, 0.2, 1),
                "real_price": calculate_service_price('confort', distance_km)
            },
            {
                "id": "moto",
                "name": "Moto",
                "icon": "🏍️",
                "price": f"{calculate_service_price('moto', distance_km):,} KMF",
                "desc": "Rapide • Économique • Zéro bouchon",
                "color": (0.2, 0.5, 0.8, 1),
                "real_price": calculate_service_price('moto', distance_km)
            },
            {
                "id": "luxe",
                "name": "Luxe",
                "icon": "⭐",
                "price": f"{calculate_service_price('luxe', distance_km):,} KMF",
                "desc": "Haut de gamme • Service premium",
                "color": (0.7, 0.2, 0.7, 1),
                "real_price": calculate_service_price('luxe', distance_km)
            },
        ]

        self.selected_service = "standard"

        for service in self.services:
            btn = Button(
                text=f"{service['icon']}  [size=18][b]{service['name']}[/b][/size]\n[size=20][b]{service['price']}[/b][/size]\n[size=12]{service['desc']}[/size]",
                markup=True,
                size_hint=(1, None),
                height=100,  # Un peu plus haut pour le prix
                background_color=service["color"],
                background_normal="",
                color=(1, 1, 1, 1),  # Texte blanc pour tous
            )
            btn.service_id = service["id"]
            btn.service_data = service  # Stocker toutes les données
            btn.bind(on_press=self.select_and_search)  # <-- CHANGER ICI !
            services_container.add_widget(btn)

        service_box.add_widget(lbl_service)
        service_box.add_widget(services_container)

        # ========== PRIX FIXE (CALCULÉ) ==========
        price_box = BoxLayout(
            orientation="vertical", size_hint=(1, None), height=120, spacing=10
        )

        lbl_price = Label(
            text="[size=16][b]Prix estimé[/b][/size]",
            markup=True,
            halign="left",
            size_hint=(1, 0.3),
        )

        # Calculer le prix basé sur la distance
        calculated_price = self.calculate_price_from_distance()

        self.lbl_calculated_price = Label(
            text=f"[size=28][b]{calculated_price} KMF[/b][/size]",
            markup=True,
            halign="center",
            size_hint=(1, 0.5),
        )

        lbl_price_info = Label(
            text="[size=12]Prix calculé selon la distance • Pas de négociation[/size]",
            markup=True,
            size_hint=(1, 0.2),
            color=(0.5, 0.5, 0.5, 1),
        )

        price_box.add_widget(lbl_price)
        price_box.add_widget(self.lbl_calculated_price)
        price_box.add_widget(lbl_price_info)

        # Stocker le prix calculé
        self.price = calculated_price

        # ========== AUTO-ACCEPTATION ==========
        auto_box = BoxLayout(orientation="horizontal", size_hint=(1, None), height=50)

        from kivy.uix.checkbox import CheckBox

        self.cb_auto_accept = CheckBox(size_hint=(0.2, 1))
        lbl_auto = Label(
            text="[size=14]Accepter automatiquement le conducteur le plus proche[/size]",
            markup=True,
            size_hint=(0.8, 1),
            halign="left",
        )

        auto_box.add_widget(self.cb_auto_accept)
        auto_box.add_widget(lbl_auto)

        # ========== BOUTON CHERCHER ==========
        btn_search = Button(
            text="[size=20][b]CHERCHER DES OFFRES[/b][/size]",
            markup=True,
            size_hint=(1, None),
            height=70,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5},
        )

        # Ajout de tous les widgets
        main_layout.add_widget(header)
        main_layout.add_widget(dest_box)
        main_layout.add_widget(service_box)
        main_layout.add_widget(auto_box)

        scroll.add_widget(main_layout)
        self.add_widget(scroll)

    def go_back(self, instance):
        """Retour à l'écran précédent"""
        self.manager.current = "client_home"

    def select_and_search(self, instance):
        """Sélectionner un service ET lancer la recherche"""
        service_id = instance.service_id
        service_data = instance.service_data
    
        print(f"🎯 Service sélectionné : {service_id}")
        print(f"💰 Prix : {service_data['real_price']} KMF")
    
        # Stocker la sélection
        self.selected_service = service_id
        self.price = service_data['real_price']
    
        # Mettre à jour visuellement (changer couleurs)
        for child in instance.parent.children:
            if hasattr(child, 'service_id'):
                if child.service_id == service_id:
                    # Service sélectionné
                    child.background_color = (0.2, 0.4, 0.8, 1)  # Bleu foncé
                    child.color = (1, 1, 1, 1)
                else:
                    # Autres services
                    child.background_color = service_data["color"]
                    child.background_color = [c * 0.7 for c in child.background_color[:3]] + [1]  # Assombrir
                    child.color = (0.9, 0.9, 0.9, 1)
    
        # Lancer la recherche après un court délai (pour l'effet visuel)
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.launch_search(service_data), 0.3)

    def get_destination_text(self):
        """Récupérer le texte de destination"""
        if hasattr(self, 'txt_to') and self.txt_to.text:
            return self.txt_to.text
        elif hasattr(self, 'destination') and self.destination:
            return self.destination
        else:
            return "Destination sélectionnée"

    def launch_search(self, service_data):
        """Lancer la recherche - Version avec points clignotants"""
        print(f"\n{'='*60}")
        print(f"🚀 LANCEMENT RECHERCHE - {service_data['name']}")
        print(f"{'='*60}")
        
        # Coordonnées
        depart_coords = getattr(self, 'depart_coords', (-11.6980, 43.2560))
        arrivee_coords = getattr(self, 'arrivee_coords', (-11.7100, 43.2650))
        destination = self.txt_to.text if hasattr(self, 'txt_to') else ""
        
        print(f"💰 Prix: {service_data['real_price']} KMF")
        print(f"🎯 Service: {service_data['id']}")
        print(f"📍 Destination: {destination}")
        
        # CRÉER LA COURSE VIA API
        global api_client
        
        if api_client and api_client.token:
            try:
                result = api_client.demander_course(
                    depart_lat=depart_coords[0],
                    depart_lng=depart_coords[1],
                    arrivee_lat=arrivee_coords[0],
                    arrivee_lng=arrivee_coords[1],
                    prix=service_data['real_price'],
                    service=service_data['id']
                )
                
                if result.get('success'):
                    course_data = result.get('course', {})
                    course_code = course_data.get('code')
                    print(f"✅ Course créée: {course_code}")
                    
                    # Aller à l'écran d'attente
                    if "waiting_for_driver" not in self.manager.screen_names:
                        self.manager.add_widget(
                            WaitingForDriverScreen(
                                name="waiting_for_driver",
                                depart_coords=depart_coords,
                                arrivee_coords=arrivee_coords,
                                destination=destination,
                                service=service_data['id'],
                                price=service_data['real_price'],
                                course_code=course_code
                            )
                        )
                    else:
                        waiting_screen = self.manager.get_screen('waiting_for_driver')
                        waiting_screen.depart_coords = depart_coords
                        waiting_screen.arrivee_coords = arrivee_coords
                        waiting_screen.destination = destination
                        waiting_screen.service = service_data['id']
                        waiting_screen.price = service_data['real_price']
                        waiting_screen.course_code = course_code
                    
                    self.manager.current = "waiting_for_driver"
                    
                else:
                    error = result.get('error', 'Erreur inconnue')
                    print(f"❌ Échec création course: {error}")
                    self.show_error_popup(f"Erreur: {error}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                self.show_error_popup(f"Erreur: {str(e)}")
        else:
            print("⚠️ API non disponible")
            self.show_error_popup("API non disponible")
    
    def show_error_popup(self, message):
        """Afficher un popup d'erreur"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        
        popup = Popup(
            title='Erreur',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def calculate_price_from_distance(self):
        """Calculer le prix basé sur la distance RÉELLE et la catégorie"""
        # TARIFICATION PAR CATÉGORIE (KMF)
        tarifs_base = {
            'standard': 500,   # Voiture standard
            'confort': 600,    # Confort (+20%)
            'luxe': 750,       # Luxe (+50%)
            'moto': 300        # Moto (-40%)
        }
    
        tarifs_km = {
            'standard': 300,   # 300 KMF/km
            'confort': 360,    # +20%
            'luxe': 450,       # +50%
            'moto': 180        # -40%
        }
    
        # Récupérer la catégorie sélectionnée
        categorie = getattr(self, 'selected_service', 'standard')
    
        # CALCULER LA DISTANCE RÉELLE
        def haversine_distance(lat1, lon1, lat2, lon2):
            from math import radians, sin, cos, sqrt, atan2
        
            R = 6371.0  # Rayon de la Terre en km
        
            lat1_rad = radians(lat1)
            lon1_rad = radians(lon1)
            lat2_rad = radians(lat2)
            lon2_rad = radians(lon2)
        
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
        
            a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
        
            distance = R * c
            return round(distance, 2)  # 2 décimales
    
        # Calculer la distance AVEC les vraies coordonnées
        try:
            distance_km = haversine_distance(
                self.depart_coords[0], self.depart_coords[1],
                self.arrivee_coords[0], self.arrivee_coords[1]
            )
        
            # Si distance trop petite (même point), minimum 0.5km
            if distance_km < 0.1:
                distance_km = 0.5
            
        except Exception as e:
            print(f"⚠️  Erreur calcul distance: {e}")
            distance_km = 4.2  # Fallback
    
        print(f"📍 Distance RÉELLE calculée: {distance_km} km")
        print(f"📍 Départ: {self.depart_coords}")
        print(f"📍 Arrivée: {self.arrivee_coords}")
    
        # Calculer le prix
        if categorie in tarifs_base:
            base = tarifs_base[categorie]
            tarif_km = tarifs_km[categorie]
        else:
            # Fallback
            base = 500
            tarif_km = 300
    
        price = base + (distance_km * tarif_km)
    
        # Arrondir à la centaine supérieure
        price = ((price + 99) // 100) * 100
    
        print(f"💰 Calcul prix {categorie}: {base} + ({distance_km}km × {tarif_km}) = {price} KMF")
        return int(price)


from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
import random

class PointsWidget(Widget):
    """Widget qui dessine des points qui clignotent"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.points = []
        self.color_mode = 'searching'  # 'searching' ou 'found'
        self.animation_step = 0
        
        # Générer des positions aléatoires pour les points
        self.generate_points()
        
        # Animation toutes les 0.5 secondes
        Clock.schedule_interval(self.animate, 0.5)
        Clock.schedule_once(self.draw_points, 0.1)
    
    def generate_points(self):
        """Génère 12 points disposés en cercle autour du centre"""
        import math
        
        centre_x = 0.5
        centre_y = 0.5
        rayon = 0.35
        
        for i in range(12):
            angle = (i / 12) * 2 * math.pi
            # Ajouter un peu d'aléatoire
            angle += random.uniform(-0.1, 0.1)
            
            x = centre_x + rayon * math.cos(angle) + random.uniform(-0.05, 0.05)
            y = centre_y + rayon * math.sin(angle) + random.uniform(-0.05, 0.05)
            
            self.points.append({
                'pos': (x, y),
                'size': random.uniform(8, 12),
                'phase': random.uniform(0, 2*math.pi)  # Pour animation décalée
            })
    
    def set_color_mode(self, mode):
        """Changer le mode de couleur"""
        self.color_mode = mode
        self.draw_points()
    
    def animate(self, dt):
        """Animation des points (clignotement)"""
        self.animation_step += 0.2
        self.draw_points()
    
    def draw_points(self, *args):
        """Dessine les points"""
        self.canvas.clear()
        
        with self.canvas:
            # Couleur selon le mode
            if self.color_mode == 'found':
                Color(0.2, 0.8, 0.2, 1)  # Vert vif
            else:
                Color(0.2, 0.5, 0.8, 1)  # Bleu ZAHEL
            
            # Dessiner chaque point avec animation
            for point in self.points:
                # Calculer l'opacité (clignotement)
                opacity = 0.5 + 0.5 * math.sin(self.animation_step + point['phase'])
                
                # Position en pixels
                x = self.x + point['pos'][0] * self.width
                y = self.y + point['pos'][1] * self.height
                
                # Taille
                size = point['size'] * (0.8 + 0.4 * math.sin(self.animation_step * 2 + point['phase']))
                
                # Dessiner le point
                Color(0.2, 0.5, 0.8, opacity)
                Ellipse(pos=(x - size/2, y - size/2), size=(size, size))
                
                # Petit halo
                Color(0.2, 0.5, 0.8, opacity * 0.3)
                Ellipse(pos=(x - size, y - size), size=(size*2, size*2))
            
            # Texte ZAHEL au centre
            from kivy.graphics import Rectangle
            Color(1, 1, 1, 1)
            # On ne peut pas dessiner du texte facilement avec canvas,
            # on utilisera un Label séparé
            
    def on_size(self, *args):
        """Redessine quand la taille change"""
        self.draw_points()

# ==================== NOUVEL ÉCRAN D'ATTENTE AVEC POINTS CLIGNOTANTS ====================

class WaitingForDriverScreen(Screen):
    def __init__(self, **kwargs):
        # Récupérer les paramètres
        depart_coords = kwargs.pop('depart_coords', (-11.6980, 43.2560))
        arrivee_coords = kwargs.pop('arrivee_coords', (-11.7100, 43.2650))
        destination = kwargs.pop('destination', "")
        service = kwargs.pop('service', "standard")
        price = kwargs.pop('price', 0)
        course_code = kwargs.pop('course_code', None)
        
        super(WaitingForDriverScreen, self).__init__(**kwargs)
        
        # Stocker les données
        self.depart_coords = depart_coords
        self.arrivee_coords = arrivee_coords
        self.destination = destination
        self.service = service
        self.price = price
        self.course_code = course_code
        self.check_timer = None
        
        # Layout principal
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=[20, 10, 20, 20])
        
        # ========== EN-TÊTE ==========
        header = BoxLayout(size_hint=(1, 0.1))
        
        btn_back = Button(text="←", size_hint=(0.15, 1), font_size="24sp", background_color=(0.2, 0.5, 0.8, 1))
        btn_back.bind(on_press=self.go_back)
        
        lbl_title = Label(
            text="[b]RECHERCHE EN COURS[/b]",
            markup=True,
            font_size="20sp",
            halign="center",
            size_hint=(0.7, 1)
        )
        
        # Espace pour équilibrer
        spacer = Label(size_hint=(0.15, 1))
        
        header.add_widget(btn_back)
        header.add_widget(lbl_title)
        header.add_widget(spacer)
        
        # ========== ZONE DES POINTS CLIGNOTANTS ==========
        points_container = BoxLayout(
            orientation="vertical",
            size_hint=(1, 0.35),
            padding=[0, 20, 0, 20]
        )
        
        # Layout pour les points (on utilisera un canvas pour dessiner)
        self.points_widget = PointsWidget(size_hint=(1, 1))
        points_container.add_widget(self.points_widget)
        
        # ========== STATISTIQUES CONDUCTEURS ==========
        stats_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, 0.25),
            spacing=15,
            padding=[20, 10, 20, 10]
        )
        
        # Titre
        stats_box.add_widget(Label(
            text="[size=16][b]📊 CONDUCTEURS DISPONIBLES[/b][/size]",
            markup=True,
            halign="left",
            size_hint=(1, 0.3)
        ))
        
        # Statistiques
        self.stats_container = BoxLayout(orientation="vertical", size_hint=(1, 0.7), spacing=5)
        
        self.lbl_online = Label(
            text="• 0 conducteurs en ligne",
            halign="left",
            size_hint=(1, 0.33)
        )
        
        self.lbl_nearby = Label(
            text="• 0 disponibles autour de vous",
            halign="left",
            size_hint=(1, 0.33)
        )
        
        self.lbl_category = Label(
            text=f"• 0 véhicule {service.upper()}",
            halign="left",
            size_hint=(1, 0.33)
        )
        
        self.stats_container.add_widget(self.lbl_online)
        self.stats_container.add_widget(self.lbl_nearby)
        self.stats_container.add_widget(self.lbl_category)
        
        stats_box.add_widget(self.stats_container)
        
        # ========== INFORMATIONS COURSE ==========
        course_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, 0.2),
            spacing=10,
            padding=[20, 10, 20, 10]
        )
        
        # Ligne destination
        dest_row = BoxLayout(size_hint=(1, 0.33))
        dest_row.add_widget(Label(text="📍", font_size="20sp", size_hint=(0.15, 1)))
        
        dest_text = destination[:30] + "..." if len(destination) > 30 else destination
        self.lbl_dest = Label(
            text=f"[b]{dest_text}[/b]",
            markup=True,
            halign="left",
            size_hint=(0.85, 1)
        )
        dest_row.add_widget(self.lbl_dest)
        
        # Ligne service et prix
        service_row = BoxLayout(size_hint=(1, 0.33))
        
        # Icône selon service
        icons = {'standard': '🚗', 'confort': '✨', 'luxe': '⭐', 'moto': '🏍️'}
        icon = icons.get(service, '🚗')
        
        service_row.add_widget(Label(text=icon, font_size="20sp", size_hint=(0.15, 1)))
        
        self.lbl_service_price = Label(
            text=f"[b]{service.upper()} • {price:,} KMF[/b]",
            markup=True,
            halign="left",
            size_hint=(0.85, 1)
        )
        service_row.add_widget(self.lbl_service_price)
        
        course_box.add_widget(dest_row)
        course_box.add_widget(service_row)
        
        # ========== BOUTON ANNULER ==========
        btn_cancel = Button(
            text="[size=18][b]ANNULER LA RECHERCHE[/b][/size]",
            markup=True,
            size_hint=(0.8, 0.08),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5}
        )
        btn_cancel.bind(on_press=self.cancel_search)
        
        # ========== ASSEMBLAGE ==========
        main_layout.add_widget(header)
        main_layout.add_widget(points_container)
        main_layout.add_widget(stats_box)
        main_layout.add_widget(course_box)
        main_layout.add_widget(btn_cancel)
        
        self.add_widget(main_layout)
        
        print(f"🎯 Écran d'attente créé pour course {self.course_code}")
    
    def on_enter(self):
        """Quand on arrive sur l'écran"""
        print(f"🚀 WaitingForDriverScreen activé - Course: {self.course_code}")
        
        # Démarrer la vérification du statut
        self.start_checking_status()
    
    def start_checking_status(self):
        """Vérifier le statut toutes les 3 secondes"""
        from kivy.clock import Clock
        self.check_timer = Clock.schedule_interval(self.check_course_status, 3)
        # Premier check immédiat
        Clock.schedule_once(self.check_course_status, 0.5)
    
    def check_course_status(self, dt):
        """Appeler l'API pour voir le statut et les conducteurs"""
        if not self.course_code:
            print("⚠️ Pas de code course, arrêt vérification")
            self.stop_checking()
            return
        
        global api_client
        
        if not api_client or not api_client.token:
            print("⚠️ API non disponible")
            return
        
        try:
            # 1. Vérifier le statut de la course
            result = api_client.get_course_status(self.course_code)
            
            if result and result.get('success'):
                course_data = result.get('course', {})
                statut = course_data.get('statut', '')
                
                # SI CONDUCTEUR TROUVÉ
                if statut in ['acceptee', 'en_cours']:
                    conducteur = course_data.get('conducteur', {})
                    if conducteur:
                        print(f"✅ CONDUCTEUR TROUVÉ: {conducteur.get('nom')}")
                        self.stop_checking()
                        
                        # Créer le dictionnaire conducteur
                        driver_info = {
                            'nom': conducteur.get('nom', 'Conducteur'),
                            'note': conducteur.get('note_moyenne', 4.5),
                            'courses': conducteur.get('courses_effectuees', 0),
                            'vehicule': f"{conducteur.get('marque_vehicule', '')} {conducteur.get('modele_vehicule', '')}".strip(),
                            'price': self.price,
                            'plaque': conducteur.get('immatricule', 'ZH-XXXXXX'),
                            'eta': '~4 min',
                            'color': conducteur.get('couleur_vehicule', '')
                        }
                        
                        # Aller à l'écran de suivi
                        self.go_to_tracking(driver_info)
                        return
            
            # 2. Récupérer les stats conducteurs (même si pas de conducteur attribué)
            self.update_driver_stats()
            
        except Exception as e:
            print(f"❌ Erreur vérification: {e}")
    
    def update_driver_stats(self):
        """Mettre à jour les statistiques des conducteurs"""
        global api_client
        
        try:
            # Appel API pour compter les conducteurs
            # À adapter selon ton API réelle
            result = api_client.get_driver_stats(
                lat=self.depart_coords[0],
                lng=self.depart_coords[1],
                radius=5,
                category=self.service
            )
            
            if result and result.get('success'):
                stats = result.get('stats', {})
                
                # Mettre à jour les labels
                self.lbl_online.text = f"• {stats.get('total_online', 0)} conducteurs en ligne"
                self.lbl_nearby.text = f"• {stats.get('nearby', 0)} disponibles autour de vous"
                
                # Changer la couleur des points selon les stats
                if stats.get('nearby', 0) > 0:
                    self.points_widget.set_color_mode('found')
                else:
                    self.points_widget.set_color_mode('searching')
                
                # Mettre à jour le compteur par catégorie
                category_count = stats.get(f'category_{self.service}', 0)
                self.lbl_category.text = f"• {category_count} véhicule {self.service.upper()}"
                
        except Exception as e:
            print(f"⚠️ Erreur mise à jour stats: {e}")
    
    def go_to_tracking(self, driver_info):
        """Aller à l'écran de suivi"""
        print(f"🚗 Redirection vers suivi avec conducteur: {driver_info['nom']}")
        
        if 'driver_tracking' not in self.manager.screen_names:
            self.manager.add_widget(DriverTrackingScreen(
                name='driver_tracking',
                driver=driver_info,
                destination=self.destination,
                price=self.price,
                course_code=self.course_code
            ))
        else:
            tracking_screen = self.manager.get_screen('driver_tracking')
            tracking_screen.driver = driver_info
            tracking_screen.destination = self.destination
            tracking_screen.price = self.price
            tracking_screen.course_code = self.course_code
        
        self.manager.current = 'driver_tracking'
    
    def cancel_search(self, instance):
        """Annuler la recherche"""
        print("❌ Annulation de la recherche")
        
        global api_client
        if api_client and self.course_code:
            try:
                result = api_client.cancel_course(self.course_code)
                if result.get('success'):
                    print(f"✅ Course {self.course_code} annulée")
                else:
                    print(f"⚠️ Erreur annulation: {result.get('error')}")
            except Exception as e:
                print(f"⚠️ Exception: {e}")
        
        self.stop_checking()
        self.manager.current = 'client_home'
    
    def go_back(self, instance):
        """Retour (équivaut à annuler)"""
        self.cancel_search(instance)
    
    def stop_checking(self):
        """Arrêter la vérification périodique"""
        if self.check_timer:
            from kivy.clock import Clock
            Clock.unschedule(self.check_timer)
            self.check_timer = None
            print("⏹️ Vérification arrêtée")
    
    def on_leave(self):
        """Nettoyage en quittant"""
        self.stop_checking()


class DriverTrackingScreen(Screen):
    def __init__(self, driver=None, destination="", price=0, **kwargs):
        super(DriverTrackingScreen, self).__init__(**kwargs)

        print(f"=== DEBUG DriverTrackingScreen __init__ ===")
    
        # Force le rechargement de l'API client
        import importlib
        import sys
    
        if 'api.client' in sys.modules:
            print("🔍 Rechargement du module api.client...")
            importlib.reload(sys.modules['api.client'])
    
        # Réimporte
        from api.client import APIClient
        print(f"🔍 Version APIClient chargée: {APIClient.__module__}")
    
        # Gérer les deux formats de clés (français/anglais)
        if driver:
            # Normaliser les clés
            normalized_driver = {
                'name': driver.get('nom') or driver.get('name', 'Hassan'),
                'vehicle': driver.get('vehicule') or driver.get('vehicle', 'Hyundai Verna'),
                'plate': driver.get('plaque') or driver.get('plate', '4384 اصق'),
                'rating': driver.get('note') or driver.get('rating', 4.82),
                'trips': driver.get('courses') or driver.get('trips', 8012),
                'color': driver.get('couleur') or driver.get('color', 'Blanc'),
                'price': driver.get('price', price),
                'eta': driver.get('eta', '~4 min')
            }
            self.driver = normalized_driver
        else:
            self.driver = {
                "name": "Hassan",
                "vehicle": "Hyundai Verna",
                "plate": "4384 اصق",
                "rating": 4.82,
                "trips": 8012,
                "color": "Blanc",
            }
    
        self.destination = destination
        self.price = price
        # Connexion à l'API pour les mises à jour temps réel
        self.course_code = kwargs.get('course_code')
        self.api_token = None
        self.update_interval = None

        # Récupérer le token depuis l'application
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'client_data'):
            self.api_token = app.client_data.get('token')
            print(f"✅ TrackingScreen: Token API récupéré")
        self.eta = self.driver.get('eta', '~4 min')

        # Layout principal
        main_layout = BoxLayout(orientation="vertical", spacing=0)

        # ========== CARTE RÉELLE ==========
        map_section = BoxLayout(orientation="vertical", size_hint=(1, 0.5))

        # Utiliser la même carte que dans MapSelectionScreen
        try:
            from kivy_garden.mapview import MapView, MapMarker
            from kivy.clock import Clock
    
            # Créer la carte
            self.map_view = MapView(
                zoom=14,
                lat=-11.6980,  # Position par défaut (Moroni)
                lon=43.2560,
                size_hint=(1, 1)
            )
    
            # Marqueur conducteur (bleu)
            self.driver_marker = MapMarker(
                lat=-11.6980,
                lon=43.2560,
                source='images/driver_icon.png'  # Tu dois créer cette image
            )
    
            # Marqueur client (vert)
            self.client_marker = MapMarker(
                lat=-11.6980,
                lon=43.2560,
                source='images/client_icon.png'  # Tu dois créer cette image
            )
    
            # EXEMPLE DE CORRECTION :
            # Remplace destination_coords par la bonne variable
            if hasattr(self, 'destination_data') and self.destination_data:
                lat = self.destination_data['latitude']
                lng = self.destination_data['longitude']
            elif hasattr(self, 'arrival_coords') and self.arrival_coords:
                lat = self.arrival_coords['latitude']
                lng = self.arrival_coords['longitude']
            else:
                # Utiliser des coordonnées par défaut
                lat = -11.698
                lng = 43.256
            # AJOUTE CE CODE : Créer dest_marker
            self.dest_marker = MapMarker(
                lat=lat,
                lon=lng,
                source='images/flag_green.png'  # Assure-toi que cette image existe
            )    
    
            self.map_view.add_marker(self.driver_marker)
            self.map_view.add_marker(self.client_marker)
            self.map_view.add_marker(self.dest_marker)
    
            map_section.add_widget(self.map_view)
    
            print("✅ Carte réelle initialisée")
    
        except Exception as e:
            print(f"⚠️  Erreur carte: {e}, utilisation simulation")
            # Vérification
            print(f"🔍 Chemin images:")
            print(f"  Chemin absolu: {os.path.abspath('images/driver_icon.png')}")
            print(f"  Existe: {os.path.exists('images/driver_icon.png')}")
            # Fallback à la simulation
            map_label = Label(
                text="[size=24]🗺️\n\nCarte de suivi en temps réel\n\n"
                "📍 Conducteur: ZH-641NZZ\n"
                "🎯 Votre position\n"
                f"🚩 Destination: {destination[:20]}...\n\n"
                "(Position mise à jour toutes les 5s)",
                markup=True,
                halign="center",
                valign="middle",
                color=(0.2, 0.2, 0.2, 1),
            )
            map_section.add_widget(map_label)

        # ========== INFORMATIONS CONDUCTEUR ==========
        driver_section = BoxLayout(
            orientation="vertical", 
            size_hint=(1, 0.3),  # Un peu plus haut pour le chrono
            padding=[20, 10], 
            spacing=8  # Espacement réduit
        )

        # ----- Ligne 1 : Véhicule -----
        vehicle_row = BoxLayout(size_hint=(1, 0.2))
        self.lbl_vehicle = Label(  
            text=f'[size=18]🚗 {self.driver["color"]} {self.driver["vehicle"]}[/size]',
            markup=True,
            halign="left",
            size_hint=(0.6, 1)
        )
        self.lbl_plate = Label(  
            text=f'[size=16][b]{self.driver.get("plate", "ZH-327KYM")}[/b][/size]',
            markup=True,
            halign="right",
            size_hint=(0.4, 1)
        )
        vehicle_row.add_widget(self.lbl_vehicle) 
        vehicle_row.add_widget(self.lbl_plate)    
        driver_section.add_widget(vehicle_row)  # ← AJOUT DIRECT

        # ----- Ligne 2 : Nom et note -----
        info_row = BoxLayout(size_hint=(1, 0.2))
        self.lbl_name = Label( 
            text=f'[size=18][b]{self.driver["name"]}[/b][/size]\n'
                 f'★ {self.driver["rating"]} ({self.driver["trips"]} courses)',
            markup=True,
            halign="left",
            size_hint=(0.7, 1)
        )
        self.lbl_eta = Label( 
            text=f"[size=22][b]{self.eta}[/b][/size]",
            markup=True,
            halign="right",
            size_hint=(0.3, 1)
        )
        info_row.add_widget(self.lbl_name) 
        info_row.add_widget(self.lbl_eta)  
        driver_section.add_widget(info_row)  # ← AJOUT DIRECT

        # ----- Ligne 3 : CHRONO (NOUVEAU) -----
        chrono_box = BoxLayout(size_hint=(1, 0.15))
        self.chrono_label = Label(
            text="⏱️ Arrivée dans: --:--",
            font_size="16sp",
            bold=True,
            color=(0.2, 0.5, 0.8, 1),
            halign='center'
        )
        chrono_box.add_widget(self.chrono_label)
        driver_section.add_widget(chrono_box)  # ← AJOUT DIRECT

        # ----- Ligne 4 : Progression -----
        progress_row = BoxLayout(orientation="vertical", size_hint=(1, 0.3))
        from kivy.uix.progressbar import ProgressBar
        self.progress_bar = ProgressBar(max=100, value=25, size_hint=(1, 0.6))
        lbl_progress = Label(
            text="Le conducteur est en route",
            size_hint=(1, 0.4),
            font_size="12sp",
            color=(0.5, 0.5, 0.5, 1),
        )
        progress_row.add_widget(self.progress_bar)
        progress_row.add_widget(lbl_progress)
        driver_section.add_widget(progress_row)  # ← AJOUT DIRECT

        # ========== BOUTONS D'ACTION ==========
        actions_section = GridLayout(
            cols=3, rows=2, size_hint=(1, 0.25), padding=[20, 10], spacing=15
        )

        # Bouton 1 : Contacter
        btn_contact = Button(
            text="[size=18]📞\nContacter[/size]",
            markup=True,
            background_color=(0.2, 0.5, 0.8, 1),
        )
        btn_contact.bind(on_press=self.contact_driver)

        # Bouton 2 : Sécurité
        btn_safety = Button(
            text="[size=18]🛡️\nSécurité[/size]",
            markup=True,
            background_color=(0.8, 0.5, 0.2, 1),
        )
        btn_safety.bind(on_press=self.show_safety)

        # Bouton 3 : Remarques
        btn_remarks = Button(
            text="[size=18]📝\nRemarques[/size]",
            markup=True,
            background_color=(0.2, 0.6, 0.2, 1),
        )
        btn_remarks.bind(on_press=self.add_remarks)

        # Bouton 4 : Partager
        btn_share = Button(
            text="[size=18]📤\nPartager[/size]",
            markup=True,
            background_color=(0.6, 0.2, 0.8, 1),
        )
        btn_share.bind(on_press=self.share_ride)

        # Bouton 5 : Paiement
        btn_payment = Button(
            text="[size=18]💰\nPaiement[/size]",
            markup=True,
            background_color=(0.8, 0.2, 0.2, 1),
        )
        btn_payment.bind(on_press=self.show_payment)

        # Bouton 6 : Urgences
        btn_emergency = Button(
            text="[size=18]🚨\nUrgences[/size]",
            markup=True,
            background_color=(0.9, 0.1, 0.1, 1),
        )
        btn_emergency.bind(on_press=self.call_emergency)

        actions_section.add_widget(btn_contact)
        actions_section.add_widget(btn_safety)
        actions_section.add_widget(btn_remarks)
        actions_section.add_widget(btn_share)
        actions_section.add_widget(btn_payment)
        actions_section.add_widget(btn_emergency)

        # ========== INFORMATIONS COURSE ==========
        ride_info = BoxLayout(
            orientation="vertical", size_hint=(1, 0.15), padding=[20, 10], spacing=5
        )

        lbl_dest = Label(
            text=f"[size=16]Destination:[/size] [b]{self.destination}[/b]",
            markup=True,
            halign="left",
            size_hint=(1, 0.5),
        )

        lbl_price = Label(
            text=f"[size=18][b]Prix: {self.price} KMF[/b][/size]",
            markup=True,
            halign="left",
            size_hint=(1, 0.5),
        )

        ride_info.add_widget(lbl_dest)
        ride_info.add_widget(lbl_price)

        # ========== BOUTON ANNULER ==========
        btn_cancel = Button(
            text="[size=16]ANNULER LA COURSE[/size]",
            markup=True,
            size_hint=(1, 0.1),
            background_color=(0.8, 0.2, 0.2, 0.8),
            color=(1, 1, 1, 1),
        )
        btn_cancel.bind(on_press=self.cancel_ride)

        # Ajout de tous les widgets
        main_layout.add_widget(map_section)
        main_layout.add_widget(driver_section)
        main_layout.add_widget(actions_section)
        main_layout.add_widget(ride_info)
        main_layout.add_widget(btn_cancel)

        self.add_widget(main_layout)

        # Démarrer la simulation de progression
        from kivy.clock import Clock

        Clock.schedule_interval(self.update_progress, 0.5)

        # Mise à jour depuis l'API toutes les 5 secondes
        Clock.schedule_interval(self.update_from_api, 5)

        # Premier appel immédiat
        Clock.schedule_once(self.update_from_api, 1)

    # ========== MÉTHODES ==========

    def update_progress(self, dt):
        """Mettre à jour la progression (mix simulation + API)"""
        # 1. D'abord vérifier l'API
        self.update_from_api()
    
        # 2. Simulation seulement si pas de données API
        current_value = self.progress_bar.value
    
        if current_value < 100:
            # Simulation légère
            self.progress_bar.value = min(current_value + 0.2, 100)
        
            # Mettre à jour l'ETA basé sur la progression
            remaining = 100 - current_value
            if remaining < 10:
                self.eta = "~1 min"
            elif remaining < 30:
                self.eta = "~2 min"
            elif remaining < 50:
                self.eta = "~3 min"
            else:
                self.eta = "~4 min"

    def update_from_api(self, dt=None):
        """Mettre à jour les informations depuis l'API - AVEC CHRONO"""
        global api_client

        if not hasattr(self, 'course_code') or not self.course_code:
            print("ℹ️  Pas encore de course_code")
            return

        if not api_client:
            print("⚠️  api_client non disponible")
            return

        try:
            print(f"🔍 Mise à jour API pour course: {self.course_code}")
            result = api_client.get_course_status(self.course_code)
    
            if result and result.get('success'):
                course_data = result.get('course', {})
                statut = course_data.get('statut', '')
        
                print(f"✅ Statut reçu: {statut}")
        
                # ===== MISE À JOUR DU CHRONO =====
                if statut in ['acceptee', 'en_cours'] and course_data.get('conducteur'):
                    # Récupérer la position du conducteur
                    conducteur = course_data.get('conducteur', {})
                    lat_cond = conducteur.get('latitude')
                    lng_cond = conducteur.get('longitude')
                
                    if lat_cond and lng_cond:
                        # Calculer la distance et le temps estimé
                        from math import radians, sin, cos, sqrt, atan2
                    
                        # Position du client (point de départ)
                        lat_client = self.depart_coords[0] if hasattr(self, 'depart_coords') else -11.698
                        lng_client = self.depart_coords[1] if hasattr(self, 'depart_coords') else 43.256
                    
                        # Calcul de distance (formule de Haversine)
                        R = 6371  # Rayon Terre en km
                    
                        lat1_rad = radians(lat_cond)
                        lon1_rad = radians(lng_cond)
                        lat2_rad = radians(lat_client)
                        lon2_rad = radians(lng_client)
                    
                        dlat = lat2_rad - lat1_rad
                        dlon = lon2_rad - lon1_rad
                    
                        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
                        c = 2 * atan2(sqrt(a), sqrt(1-a))
                    
                        distance_km = R * c
                    
                        # Vitesse moyenne estimée (25 km/h en ville)
                        vitesse_kmh = 25
                        temps_minutes = (distance_km / vitesse_kmh) * 60
                    
                        # Mettre à jour le chrono
                        if temps_minutes < 1:
                            self.chrono_label.text = f"⏱️ Arrivée dans: {int(temps_minutes*60)} secondes"
                        else:
                            self.chrono_label.text = f"⏱️ Arrivée dans: {int(temps_minutes)} min"
                    else:
                        # Pas de GPS, utiliser l'ETA de l'API
                        eta = conducteur.get('eta', '~4 min')
                        self.chrono_label.text = f"⏱️ Arrivée dans: {eta}"
                else:
                    # Si pas encore de conducteur ou pas en route
                    self.chrono_label.text = "⏱️ Arrivée dans: --:--"
        
                # ===== MISE À JOUR DE LA BARRE DE PROGRESSION =====
                # Mettre à jour la barre de progression selon le statut
                if statut == 'en_attente':
                    self.progress_bar.value = 10
                elif statut == 'acceptee':
                    self.progress_bar.value = 25
                elif statut == 'en_cours':
                    self.progress_bar.value = 50
                elif statut == 'terminee':
                    self.progress_bar.value = 100
            
                # ===== MISE À JOUR DES INFOS CONDUCTEUR =====
                conducteur = course_data.get('conducteur', {})
                if conducteur:
                    print(f"✅ Données conducteur: {conducteur}")
            
                    # Mettre à jour les labels
                    if hasattr(self, 'lbl_name'):
                        nom = conducteur.get('nom', 'Inconnu')
                        note = conducteur.get('note_moyenne', 5.0)
                        courses = conducteur.get('courses_effectuees', 0)
                        self.lbl_name.text = f'[size=22][b]{nom}[/b][/size]\n★ {note} ({courses} courses)'
            
                    if hasattr(self, 'lbl_vehicle'):
                        marque = conducteur.get('marque_vehicule', '')
                        modele = conducteur.get('modele_vehicule', '')
                        couleur = conducteur.get('couleur_vehicule', '')
                        self.lbl_vehicle.text = f'[size=20]🚗 {couleur} {marque} {modele}[/size]'
            
                    if hasattr(self, 'lbl_plate'):
                        plaque = conducteur.get('immatricule', '')
                        self.lbl_plate.text = f'[size=20][b]{plaque}[/b][/size]'
            
                    # Mettre à jour la position sur la carte
                    if hasattr(self, 'driver_marker'):
                        lat = conducteur.get('latitude')
                        lng = conducteur.get('longitude')
                        if lat and lng:
                            print(f"📍 Mise à jour position: ({lat}, {lng})")
                            self.driver_marker.lat = lat
                            self.driver_marker.lon = lng
                    
                            # Centrer la carte sur le conducteur
                            if hasattr(self, 'map_view'):
                                self.map_view.center_on(lat, lng)
            else:
                print(f"⚠️ Erreur API: {result.get('error') if result else 'No response'}")
        
        except Exception as e:
            print(f"❌ Erreur dans update_from_api: {e}")

    def contact_driver(self, instance):
        """Contacter le conducteur"""
        print(f"Contacter le conducteur: {self.driver['name']}")
        # À venir : intégration téléphone/SMS

    def show_safety(self, instance):
        """Afficher les fonctionnalités de sécurité"""
        print("Affichage des fonctionnalités de sécurité")
        self.show_safety_popup()

    def add_remarks(self, instance):
        """Ajouter des remarques pour le conducteur"""
        print("Ajout de remarques pour le conducteur")
        # À venir : popup de saisie

    def share_ride(self, instance):
        """Partager les détails de la course"""
        print("Partage des détails de la course")
        share_text = f"Je suis en route avec ZAHEL. Conducteur: {self.driver['name']}, ETA: {self.eta}"
        print(f"Texte à partager: {share_text}")

    def show_payment(self, instance):
        """Afficher les détails du paiement"""
        print(f"Détails du paiement: {self.price} KMF")
        # Popup avec plus d'informations
        from kivy.uix.popup import Popup

        content = BoxLayout(orientation="vertical", padding=20, spacing=15)

        lbl = Label(
            text=f"[size=20][b]Paiement[/b][/size]\n\n"
            f"Montant: [b]{self.price} KMF[/b]\n"
            f"Mode: 💵 Espèces\n"
            f"Statut: À payer à la fin du trajet\n\n"
            f"Options disponibles:\n"
            f"• Espèces\n"
            f"• Mobile Money (à venir)\n"
            f"• Carte bancaire (à venir)",
            markup=True,
            halign="center",
        )

        btn_close = Button(text="Fermer", size_hint=(0.6, None), height=50)

        def close_popup(instance):
            popup.dismiss()

        btn_close.bind(on_press=close_popup)

        content.add_widget(lbl)
        content.add_widget(btn_close)

        popup = Popup(
            title="Détails du paiement", content=content, size_hint=(0.8, 0.6)
        )
        popup.open()

    def call_emergency(self, instance):
        """Appeler les urgences"""
        print("Appel des services d'urgence")
        # À venir : intégration téléphone

    def cancel_ride(self, instance):
        """Annuler la course avec règles ZAHEL - VERSION CORRIGÉE"""
        print("📋 Tentative d'annulation...")
    
        # Vérifier si la course a déjà commencé
        if self.progress_bar.value > 30:
            # Course en cours - ne peut pas annuler
            self.show_cancel_error("❌ Impossible d'annuler", 
                                   "La course est déjà en cours.\n"
                                   "Vous ne pouvez pas annuler maintenant.")
        else:
            # Course pas encore commencée (en route)
            self.confirm_cancellation()

    def show_cancel_error(self, title, message):
        """Afficher une erreur d'annulation avec un message clair"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
    
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        content.add_widget(Label(
            text=message,
            halign='center',
            font_size='16sp'
        ))
    
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 0.2, 1)
        )
    
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
    
        btn_ok.bind(on_press=popup.dismiss)
        content.add_widget(btn_ok)
        popup.open()

    def confirm_cancellation(self):
        """Confirmer l'annulation avec un popup clair"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button

        content = BoxLayout(orientation='vertical', padding=20, spacing=15)

        content.add_widget(Label(
            text="[size=18]Confirmer l'annulation ?[/size]\n\n"
                 "• Annulation gratuite (course non commencée)\n"
                 "• Le conducteur sera notifié",
            markup=True,
            halign='center'
        ))

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        btn_no = Button(
            text="❌ NON, CONTINUER",
            background_color=(0.2, 0.6, 0.2, 1)
        )
    
        btn_yes = Button(
            text="✅ OUI, ANNULER",
            background_color=(0.8, 0.2, 0.2, 1)
        )

        popup = Popup(
            title="Annulation de course",
            content=content,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )

        def do_cancel(inst):
            popup.dismiss()
            self.process_cancellation()

        def do_not_cancel(inst):
            popup.dismiss()

        btn_yes.bind(on_press=do_cancel)
        btn_no.bind(on_press=do_not_cancel)

        btn_layout.add_widget(btn_no)
        btn_layout.add_widget(btn_yes)
        content.add_widget(btn_layout)

        popup.open()

    def process_cancellation(self):
        """Traiter l'annulation effective"""
        print("✅ Annulation confirmée")
    
        # Appeler l'API pour annuler
        global api_client
        if api_client and hasattr(self, 'course_code'):
            try:
                result = api_client.cancel_course(self.course_code)
                if result.get('success'):
                    print(f"✅ Course {self.course_code} annulée")
                    self.show_cancel_success("Course annulée avec succès")
                else:
                    print(f"⚠️ Erreur: {result.get('error')}")
                    self.show_cancel_error("Erreur", result.get('error', 'Erreur inconnue'))
            except Exception as e:
                print(f"❌ Exception: {e}")
                self.show_cancel_error("Erreur", str(e))
    
        # Retour à l'accueil après 2 secondes
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.go_home(), 2)

    def show_cancel_success(self, message):
        """Afficher un message de succès"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
    
        popup = Popup(
            title='✅ Annulation réussie',
            content=Label(text=message),
            size_hint=(0.7, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)

    def go_home(self):
        """Retour à l'accueil"""
        self.manager.current = 'client_home'

    def show_safety_popup(self):
        """Afficher le popup de sécurité (comme PDF page 15)"""
        from kivy.uix.popup import Popup
        from kivy.uix.gridlayout import GridLayout

        content = BoxLayout(orientation="vertical", padding=20, spacing=15)

        # Titre
        lbl_title = Label(
            text="[size=22][b]Fonctionnalités de sécurité[/b][/size]",
            markup=True,
            halign="center",
        )

        # Vérifications du conducteur
        checks_box = BoxLayout(orientation="vertical", spacing=10)

        checks = [
            ("✅", "Vérification d'identité", "Photo et informations vérifiées"),
            ("✅", "Permis de conduire", "Validé et à jour"),
            ("✅", "Casier judiciaire", "Aucun casier"),
            ("✅", "Véhicule", "Contrôle technique valide"),
            ("🔒", "Trajet partageable", "Partagez votre trajet en temps réel"),
            ("🚨", "Bouton d'urgence", "Accès rapide aux services"),
        ]

        for icon, title, desc in checks:
            check_row = BoxLayout(size_hint=(1, None), height=50)
            lbl_icon = Label(text=icon, size_hint=(0.1, 1), font_size="20sp")
            lbl_check = Label(
                text=f"[b]{title}[/b]\n[size=12]{desc}[/size]",
                markup=True,
                size_hint=(0.9, 1),
                halign="left",
            )
            check_row.add_widget(lbl_icon)
            check_row.add_widget(lbl_check)
            checks_box.add_widget(check_row)

        # Bouton appeler urgences
        btn_emergency = Button(
            text="[size=18]🚨 APPELER 122 (URGENCES)[/size]",
            markup=True,
            size_hint=(1, None),
            height=60,
            background_color=(0.9, 0.1, 0.1, 1),
        )

        # Bouton fermer
        btn_close = Button(
            text="Fermer", size_hint=(0.5, None), height=50, pos_hint={"center_x": 0.5}
        )

        def close_popup(instance):
            popup.dismiss()

        btn_close.bind(on_press=close_popup)

        content.add_widget(lbl_title)
        content.add_widget(checks_box)
        content.add_widget(btn_emergency)
        content.add_widget(btn_close)

        popup = Popup(title="Sécurité ZAHEL", content=content, size_hint=(0.9, 0.8))
        popup.open()

# Fonction utilitaire GLOBALE (hors de toute classe)
def ouvrir_whatsapp(numero, message):
    """
    Ouvre WhatsApp avec un numéro et message pré-rempli
    Format: whatsapp://send?phone=269XXXXXXXX&text=message_encoder
    """
    try:
        # Nettoyer le numéro (garder que les chiffres)
        numero_propre = ''.join(filter(str.isdigit, numero))
        
        # Encoder le message pour URL
        message_encoder = quote(message)
        
        # URL pour WhatsApp
        url = f"whatsapp://send?phone={numero_propre}&text={message_encoder}"
        
        print(f"📲 Ouverture WhatsApp: {url[:50]}...")
        
        # Ouvrir WhatsApp
        webbrowser.open(url)
        return True
        
    except Exception as e:
        print(f"❌ Erreur ouverture WhatsApp: {e}")
        return False


class ZAHELApp(App):
    def build(self):
        print(f"\n{'='*60}")
        print(f"🚀 LANCEMENT ZAHEL - MODE {'CONDUCTEUR' if IS_DRIVER_MODE else 'CLIENT'}")
        print(f"{'='*60}\n")
    
        # Créer le ScreenManager
        self.sm = ScreenManager()

        # ✅ LOGIQUE MODIFIÉE : CRÉER LES ÉCRANS SELON LE MODE
    
        if IS_DRIVER_MODE:
            # MODE CONDUCTEUR SEULEMENT
            print("🎯 Configuration pour MODE CONDUCTEUR")
        
            # Écrans conducteur uniquement
            self.sm.add_widget(LoginScreen(name="driver_login"))
            self.sm.add_widget(DriverRegisterScreen(name="driver_register")) 
            self.sm.add_widget(DashboardScreen(name="dashboard"))
            self.sm.add_widget(CoursesScreen(name="courses"))
            self.sm.add_widget(AmendesScreen(name='amendes'))
            self.sm.add_widget(NavigationScreen(name="navigation"))
        
            # Écran par défaut
            self.sm.current = "login"
        
        else:
            # MODE CLIENT (par défaut)
            print("🎯 Configuration pour MODE CLIENT")
        
            # Tous les écrans
            self.sm.add_widget(SelectionScreen(name="selection"))
        
            # Écrans client
            self.sm.add_widget(ClientLoginScreen(name="client_login"))
            self.sm.add_widget(ClientRegisterScreen(name="client_register"))
            self.sm.add_widget(ClientHomeScreen(name="client_home"))
            self.sm.add_widget(MapSelectionScreen(name='map_selection'))
            self.sm.add_widget(OrderRideScreen(
                name='order_ride',
                depart_coords=(-11.6980, 43.2560),
                arrivee_coords=(-11.7100, 43.2650),
                destination=""
            ))
            self.sm.add_widget(WaitingForDriverScreen(name="waiting_for_driver"))
            
            self.sm.add_widget(DriverTrackingScreen(name="driver_tracking"))
        
            # Écrans conducteur (accessibles via sélection)
            self.sm.add_widget(LoginScreen(name="driver_login"))
            self.sm.add_widget(DriverRegisterScreen(name="driver_register")) 
            self.sm.add_widget(DashboardScreen(name="dashboard"))
            self.sm.add_widget(CoursesScreen(name="courses"))
            self.sm.add_widget(AmendesScreen(name='amendes'))
            self.sm.add_widget(NavigationScreen(name="navigation"))
        
            # Écran par défaut
            self.sm.current = "selection"

        # RESTAURER LA SESSION APRÈS avoir créé tous les écrans
        if self.restore_session():
            # Si session restaurée, aller à l'écran approprié
            from kivy.clock import Clock
            Clock.schedule_once(self.go_to_appropriate_screen, 0.5)

        return self.sm
    
    def go_to_appropriate_screen(self, dt):
        """Aller à l'écran approprié selon le type d'utilisateur et le mode"""
        print(f"\n{'='*60}")
        print(f"🎯 DEBUG: go_to_appropriate_screen appelé")
        print(f"🎯 DEBUG: Écran actuel: {self.sm.current}")
        print(f"🎯 DEBUG: Mode: {'CONDUCTEUR' if IS_DRIVER_MODE else 'CLIENT'}")
        print(f"🎯 DEBUG: Client data: {hasattr(self, 'client_data')}")
        print(f"🎯 DEBUG: Conducteur data: {hasattr(self, 'conducteur_data')}")

        if IS_DRIVER_MODE:
            # MODE CONDUCTEUR
            print(f"🎯 MODE CONDUCTEUR détecté")
            if hasattr(self, 'conducteur_data'):
                print(f"🎯 Redirection vers dashboard")
                self.sm.current = 'dashboard'
            else:
                print(f"🎯 Reste sur login (pas de données conducteur)")
                self.sm.current = 'login'

        else:
            # MODE CLIENT
            print(f"🎯 MODE CLIENT détecté")
        
            # NE PAS REDIRIGER SI DÉJÀ SUR BON ÉCRAN
            if self.sm.current in ['client_home', 'order_ride', 'search_drivers', 'driver_tracking']:
                print(f"🎯 Déjà sur écran client {self.sm.current}, pas de redirection")
                return
        
            if hasattr(self, 'client_data'):
                print(f"🎯 Redirection vers client_home")
                self.sm.current = 'client_home'
            
                # IMPORTANT : NE PAS APPELER order_ride ICI !
                # Juste afficher l'accueil, attendre l'utilisateur
                print(f"🎯 Affichage accueil client - Attente action utilisateur")
            
            elif hasattr(self, 'conducteur_data'):
                print(f"🎯 Redirection vers dashboard (mode client mais données conducteur)")
                self.sm.current = 'dashboard'
            else:
                print(f"🎯 Reste sur selection (pas de session)")
    
        print(f"{'='*60}\n")

    def restore_session(self):
        """Restaurer la session au démarrage - VERSION AVEC RAJEUNISSEMENT"""
        global api_client, API_MODULE_EXISTS

        # ✅ VIDER LES ANCIENNES DONNÉES
        if hasattr(self, 'client_data'):
            self.client_data = {}
        if hasattr(self, 'conducteur_data'):
            self.conducteur_data = {}
    
        try:
            import json
            import time
            import os
        
            if not os.path.exists('session.json'):
                print(f"📱 Pas de fichier session.json trouvé")
                return False
        
            with open('session.json', 'r') as f:
                session_data = json.load(f)
                user_type = session_data.get('user_type')
                identifier = session_data.get('identifier')
                token = session_data.get('token')
                timestamp = session_data.get('timestamp', 0)
        
                print(f"📱 Fichier session trouvé:")
                print(f"   Type: {user_type}")
                print(f"   Identifiant: {identifier}")
                print(f"   Token: {token}")
                print(f"   Timestamp: {timestamp}")
        
                # ✅ 1. VÉRIFIER TOKEN VALIDE
                global api_client
                if not token or token == '':
                    print("❌ Token vide ou invalide dans la session")
                    print("❌ Suppression de la session corrompue")
                    os.remove('session.json')
                    return False
        
                # ✅ 2. VÉRIFIER COHÉRENCE MODE
                if IS_DRIVER_MODE and user_type != 'conducteur':
                    print("⚠️  Mode CONDUCTEUR mais session CLIENT - Ignorée")
                    os.remove('session.json')
                    return False
                elif not IS_DRIVER_MODE and user_type != 'client':
                    print("⚠️  Mode CLIENT mais session CONDUCTEUR - Ignorée")
                    os.remove('session.json')
                    return False
        
                # ✅ 3. VÉRIFIER EXPIRATION (1 an)
                if time.time() - timestamp > 31536000:  # 1 an au lieu de 7 jours
                    print("📱 Session expirée (plus d'1 an)")
                    os.remove('session.json')
                    return False
        
                # ========== ✅ 4. RAJEUNIR LA SESSION ==========
                # Cette partie est NOUVELLE - Elle met à jour le timestamp
                session_data['timestamp'] = time.time()
                with open('session.json', 'w') as f:
                    json.dump(session_data, f)
            
                # Afficher la nouvelle date
                nouvelle_date = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(session_data['timestamp']))
                print(f"🔄 Session rajeunie - {nouvelle_date}")
                # ==============================================
        
                # ✅ 5. CONFIGURER SELON LE TYPE
                if user_type == 'client':
                    print("✅ Session client valide")
            
                    # Stocker dans app.client_data
                    self.client_data = {
                        'token': token,
                        'telephone': identifier,
                        'user_type': user_type,
                        'timestamp': session_data['timestamp']
                    }
            
                    # Configurer le token dans api_client
                    if api_client and API_MODULE_EXISTS:
                        print(f"🔧 Configuration api_client avec token: {token}")
                        success = api_client.set_token(token, 'client')
                        if success:
                            print(f"✅ api_client configuré")
                            print(f"   Token: {api_client.token}")
                            print(f"   User type: {api_client.user_type}")
                        else:
                            print(f"❌ Erreur configuration api_client")
                 
                    return True
        
                elif user_type == 'conducteur':
                    print("✅ Session conducteur valide")
            
                    # Stocker dans app.conducteur_data
                    self.conducteur_data = {
                        'token': token,
                        'immatricule': identifier,
                        'user_type': user_type,
                        'timestamp': session_data['timestamp']
                    }
                    self.immatricule = identifier
            
                    # Configurer le token dans api_client
                    if api_client and API_MODULE_EXISTS:
                        print(f"🔧 Configuration api_client avec token: {token}")
                        success = api_client.set_token(token, 'conducteur')
                        if success:
                            print(f"✅ api_client configuré")
                        else:
                            print(f"❌ Erreur configuration api_client")
            
                    return True
            
        except Exception as e:
            print(f"📱 Erreur lecture session: {e}")
            return False

    import webbrowser
    from urllib.parse import quote


if __name__ == "__main__":
    ZAHELApp().run()
