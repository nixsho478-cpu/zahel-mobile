# i18n/translations.py - Fichier de traduction ZAHEL

class Translations:
    """Gestionnaire de traductions Français/Anglais"""
    
    def __init__(self, lang='fr'):
        self.lang = lang  # 'fr' ou 'en'
        
        # Dictionnaire des traductions
        self.strings = {
            'fr': {
                # ===== GÉNÉRAL =====
                'app_name': 'ZAHEL',
                'loading': 'Chargement...',
                'error': 'Erreur',
                'success': 'Succès',
                'cancel': 'Annuler',
                'confirm': 'Confirmer',
                'back': 'Retour',
                'refresh': 'Rafraîchir',
                'save': 'Enregistrer',
                'delete': 'Supprimer',
                'edit': 'Modifier',
                'search': 'Rechercher',
                'no_results': 'Aucun résultat',
                'network_error': 'Erreur de connexion',
                'retry': 'Réessayer',
                'version': 'Version 1.0',
                
                # ===== AUTHENTIFICATION =====
                'login': 'Connexion',
                'logout': 'Déconnexion',
                'register': 'Inscription',
                'username': 'Nom d\'utilisateur',
                'password': 'Mot de passe',
                'confirm_password': 'Confirmer le mot de passe',
                'forgot_password': 'Mot de passe oublié ?',
                'phone_number': 'Numéro de téléphone',
                'email': 'Email',
                
                # ===== SÉLECTION MODE =====
                'select_mode': 'Choisissez votre mode',
                'driver_mode': 'CONDUCTEUR',
                'client_mode': 'CLIENT',
                
                # ===== CLIENT =====
                'where_to': 'Où allez-vous ?',
                'destination': 'Destination',
                'departure': 'Départ',
                'order_ride': 'COMMANDER UNE COURSE',
                'my_rides': 'Mes courses',
                'my_account': 'Mon compte',
                'my_addresses': 'Mes adresses',
                'add_address': 'Ajouter une adresse',
                'home': 'Accueil',
                'work': 'Travail',
                'other': 'Autre',
                'save_address': 'Enregistrer l\'adresse',
                'select_on_map': 'Sélectionner sur la carte',
                'use_my_location': 'Utiliser ma position',
                
                # ===== SERVICES =====
                'standard': 'Standard',
                'confort': 'Confort',
                'luxury': 'Luxe',
                'moto': 'Moto',
                'standard_desc': 'Voiture économique',
                'confort_desc': 'Voitures récentes',
                'luxury_desc': 'Service premium',
                'moto_desc': 'Rapide et économique',
                'estimated_price': 'Prix estimé',
                'search_driver': 'RECHERCHER UN CONDUCTEUR',
                'cancel_search': 'ANNULER LA RECHERCHE',
                
                # ===== CONDUCTEUR EN ATTENTE =====
                'searching': 'RECHERCHE EN COURS',
                'drivers_online': 'conducteurs en ligne',
                'drivers_around': 'disponibles autour de vous',
                'vehicles_available': 'véhicule(s) disponible(s)',
                
                # ===== SUIVI COURSE =====
                'driver_found': 'CONDUCTEUR TROUVÉ',
                'driver_on_way': 'Le conducteur est en route',
                'estimated_arrival': 'Arrivée estimée',
                'contact_driver': 'Contacter',
                'safety': 'Sécurité',
                'share_ride': 'Partager',
                'payment': 'Paiement',
                'emergency': 'Urgences',
                'cancel_ride': 'ANNULER LA COURSE',
                'ride_completed': 'Course terminée',
                
                # ===== CONDUCTEUR =====
                'driver_login': 'Connexion Conducteur',
                'driver_register': 'Inscription Conducteur',
                'immatriculation': 'Immatriculation',
                'personal_info': 'Informations personnelles',
                'full_name': 'Nom complet',
                'nationality': 'Nationalité',
                'id_number': "Numéro d'identité",
                'vehicle_info': 'Informations véhicule',
                'brand': 'Marque',
                'model': 'Modèle',
                'color': 'Couleur',
                'plate': 'Plaque',
                'category': 'Catégorie',
                'register_driver': "S'INSCRIRE",
                
                # ===== DASHBOARD CONDUCTEUR =====
                'dashboard': 'Tableau de bord',
                'statistics': 'Statistiques',
                'rides': 'courses',
                'earnings': 'gains',
                'rating': 'note',
                'available': 'Disponible',
                'unavailable': 'Indisponible',
                'become_unavailable': 'DEVENIR INDISPONIBLE',
                'become_available': 'DEVENIR DISPONIBLE',
                'see_rides': 'VOIR LES COURSES',
                'my_fines': 'MES AMENDES',
                'my_profile': 'MON PROFIL',
                'subscription': 'Abonnement',
                'rides_left': 'courses restantes',
                'last_rides': 'DERNIÈRE COURSE !',
                'subscription_expired': 'Abonnement terminé',
                'renew': 'Renouveler',
                
                # ===== COURSES DISPONIBLES =====
                'available_rides': 'Courses disponibles',
                'no_rides': 'Aucune course disponible',
                'accept': 'ACCEPTER',
                'accept_ride': 'ACCEPTER CETTE COURSE',
                'pickup': 'Prise en charge',
                'dropoff': 'Destination',
                'distance': 'Distance',
                'duration': 'Durée',
                'price': 'Prix',
                'client': 'Client',
                'call_client': 'Appeler le client',
                
                # ===== AMENDES =====
                'fines_collected': 'Amendes collectées',
                'total_to_pay': 'Total à verser',
                'pay_to_agency': 'VERSER À L\'AGENCE',
                'fine_amount': 'Montant',
                'fine_date': 'Date',
                'fine_status': 'Statut',
                'fine_paid': 'Payée',
                'fine_pending': 'En attente',
                'confirm_payment': 'Confirmer le versement',
                
                # ===== PROFIL =====
                'profile': 'Profil',
                'my_history': 'Mon historique',
                'settings': 'Paramètres',
                'notifications': 'Notifications',
                'language': 'Langue',
                'change_password': 'Changer mot de passe',
                'privacy': 'Confidentialité',
                'terms': "Conditions d'utilisation",
                'help': 'Aide',
                'about': 'À propos',
                
                # ===== HISTORIQUE =====
                'history': 'Historique',
                'month': 'Mois',
                'total_rides': 'Total courses',
                'total_earnings': 'Gains totaux',
                'total_taxes': 'Taxes totales',
                'completed': 'Terminée',
                'cancelled': 'Annulée',
                'in_progress': 'En cours',
                
                # ===== PARAMÈTRES LANGUE =====
                'select_language': 'Choisir la langue',
                'french': 'Français',
                'english': 'English',
                
                # ===== MESSAGES =====
                'welcome_back': 'Bon retour parmi nous !',
                'registration_success': 'Inscription réussie',
                'login_success': 'Connexion réussie',
                'logout_success': 'Déconnexion réussie',
                'operation_success': 'Opération réussie',
                'confirm_logout': 'Êtes-vous sûr de vouloir vous déconnecter ?',
                'confirm_delete': 'Confirmer la suppression ?',
                'delete_address_confirm': 'Cette action est irréversible.',
                
                # ===== WHATSAPP =====
                'whatsapp_required': 'VÉRIFICATION REQUISE',
                'send_photos': 'ENVOYER LES PHOTOS',
                'send_on_whatsapp': 'ENVOYER SUR WHATSAPP',
                'later': 'Plus tard',
                'verification_pending': 'Vérification en attente',
                'verification_time': 'Délai 2-4h',

                # Dans la section FRANÇAIS
                'min': 'min',
                'driver': 'Conducteur',
                'vehicle': 'Véhicule',
                'white': 'Blanc',
                'tracking': 'Suivi en direct',
                'contact_driver': 'Contacter',
                'safety': 'Sécurité',
                'remarks': 'Remarques',
                'share_ride': 'Partager',
                'payment': 'Paiement',
                'emergency': 'Urgences',
                'destination': 'Destination',
                'price': 'Prix',
                'cancel_ride': 'ANNULER LA COURSE',
                'driver_on_way': 'Le conducteur est en route',
                'estimated_arrival': 'Arrivée estimée',
            },
            
            'en': {
                # ===== GENERAL =====
                'app_name': 'ZAHEL',
                'loading': 'Loading...',
                'error': 'Error',
                'success': 'Success',
                'cancel': 'Cancel',
                'confirm': 'Confirm',
                'back': 'Back',
                'refresh': 'Refresh',
                'save': 'Save',
                'delete': 'Delete',
                'edit': 'Edit',
                'search': 'Search',
                'no_results': 'No results',
                'network_error': 'Network error',
                'retry': 'Retry',
                'version': 'Version 1.0',
                
                # ===== AUTHENTICATION =====
                'login': 'Login',
                'logout': 'Logout',
                'register': 'Register',
                'username': 'Username',
                'password': 'Password',
                'confirm_password': 'Confirm password',
                'forgot_password': 'Forgot password?',
                'phone_number': 'Phone number',
                'email': 'Email',
                
                # ===== MODE SELECTION =====
                'select_mode': 'Choose your mode',
                'driver_mode': 'DRIVER',
                'client_mode': 'CLIENT',
                
                # ===== CLIENT =====
                'where_to': 'Where to?',
                'destination': 'Destination',
                'departure': 'Departure',
                'order_ride': 'ORDER A RIDE',
                'my_rides': 'My rides',
                'my_account': 'My account',
                'my_addresses': 'My addresses',
                'add_address': 'Add address',
                'home': 'Home',
                'work': 'Work',
                'other': 'Other',
                'save_address': 'Save address',
                'select_on_map': 'Select on map',
                'use_my_location': 'Use my location',
                
                # ===== SERVICES =====
                'standard': 'Standard',
                'confort': 'Comfort',
                'luxury': 'Luxury',
                'moto': 'Moto',
                'standard_desc': 'Economy car',
                'confort_desc': 'Recent cars',
                'luxury_desc': 'Premium service',
                'moto_desc': 'Fast & cheap',
                'estimated_price': 'Estimated price',
                'search_driver': 'SEARCH DRIVER',
                'cancel_search': 'CANCEL SEARCH',
                
                # ===== WAITING FOR DRIVER =====
                'searching': 'SEARCHING',
                'drivers_online': 'drivers online',
                'drivers_around': 'available near you',
                'vehicles_available': 'vehicle(s) available',
                
                # ===== RIDE TRACKING =====
                'driver_found': 'DRIVER FOUND',
                'driver_on_way': 'Driver is on the way',
                'estimated_arrival': 'Estimated arrival',
                'contact_driver': 'Contact',
                'safety': 'Safety',
                'share_ride': 'Share',
                'payment': 'Payment',
                'emergency': 'Emergency',
                'cancel_ride': 'CANCEL RIDE',
                'ride_completed': 'Ride completed',
                
                # ===== DRIVER =====
                'driver_login': 'Driver Login',
                'driver_register': 'Driver Registration',
                'immatriculation': 'License plate',
                'personal_info': 'Personal info',
                'full_name': 'Full name',
                'nationality': 'Nationality',
                'id_number': 'ID number',
                'vehicle_info': 'Vehicle info',
                'brand': 'Brand',
                'model': 'Model',
                'color': 'Color',
                'plate': 'Plate',
                'category': 'Category',
                'register_driver': 'REGISTER',
                
                # ===== DRIVER DASHBOARD =====
                'dashboard': 'Dashboard',
                'statistics': 'Statistics',
                'rides': 'rides',
                'earnings': 'earnings',
                'rating': 'rating',
                'available': 'Available',
                'unavailable': 'Unavailable',
                'become_unavailable': 'GO OFFLINE',
                'become_available': 'GO ONLINE',
                'see_rides': 'SEE RIDES',
                'my_fines': 'MY FINES',
                'my_profile': 'MY PROFILE',
                'subscription': 'Subscription',
                'rides_left': 'rides left',
                'last_rides': 'LAST RIDE !',
                'subscription_expired': 'Subscription expired',
                'renew': 'Renew',
                
                # ===== AVAILABLE RIDES =====
                'available_rides': 'Available rides',
                'no_rides': 'No rides available',
                'accept': 'ACCEPT',
                'accept_ride': 'ACCEPT THIS RIDE',
                'pickup': 'Pickup',
                'dropoff': 'Dropoff',
                'distance': 'Distance',
                'duration': 'Duration',
                'price': 'Price',
                'client': 'Client',
                'call_client': 'Call client',
                
                # ===== FINES =====
                'fines_collected': 'Collected fines',
                'total_to_pay': 'Total to pay',
                'pay_to_agency': 'PAY TO AGENCY',
                'fine_amount': 'Amount',
                'fine_date': 'Date',
                'fine_status': 'Status',
                'fine_paid': 'Paid',
                'fine_pending': 'Pending',
                'confirm_payment': 'Confirm payment',
                
                # ===== PROFILE =====
                'profile': 'Profile',
                'my_history': 'My history',
                'settings': 'Settings',
                'notifications': 'Notifications',
                'language': 'Language',
                'change_password': 'Change password',
                'privacy': 'Privacy',
                'terms': 'Terms of use',
                'help': 'Help',
                'about': 'About',
                
                # ===== HISTORY =====
                'history': 'History',
                'month': 'Month',
                'total_rides': 'Total rides',
                'total_earnings': 'Total earnings',
                'total_taxes': 'Total taxes',
                'completed': 'Completed',
                'cancelled': 'Cancelled',
                'in_progress': 'In progress',
                
                # ===== LANGUAGE SETTINGS =====
                'select_language': 'Select language',
                'french': 'Français',
                'english': 'English',
                
                # ===== MESSAGES =====
                'welcome_back': 'Welcome back!',
                'registration_success': 'Registration successful',
                'login_success': 'Login successful',
                'logout_success': 'Logout successful',
                'operation_success': 'Operation successful',
                'confirm_logout': 'Are you sure you want to logout?',
                'confirm_delete': 'Confirm deletion?',
                'delete_address_confirm': 'This action is irreversible.',
                
                # ===== WHATSAPP =====
                'whatsapp_required': 'VERIFICATION REQUIRED',
                'send_photos': 'SEND PHOTOS',
                'send_on_whatsapp': 'SEND ON WHATSAPP',
                'later': 'Later',
                'verification_pending': 'Verification pending',
                'verification_time': '2-4h delay',

                # Dans la section ANGLAIS
                'min': 'min',
                'driver': 'Driver',
                'vehicle': 'Vehicle',
                'white': 'White',
                'tracking': 'Live tracking',
                'contact_driver': 'Contact',
                'safety': 'Safety',
                'remarks': 'Remarks',
                'share_ride': 'Share',
                'payment': 'Payment',
                'emergency': 'Emergency',
                'destination': 'Destination',
                'price': 'Price',
                'cancel_ride': 'CANCEL RIDE',
                'driver_on_way': 'Driver is on the way',
                'estimated_arrival': 'Estimated arrival',
            }
        }
    
    def get(self, key, **kwargs):
        """Récupère une traduction avec formatage optionnel"""
        try:
            text = self.strings[self.lang].get(key, key)
            if kwargs:
                text = text.format(**kwargs)
            return text
        except:
            return key
    
    def set_language(self, lang):
        """Change la langue (fr ou en)"""
        if lang in ['fr', 'en']:
            self.lang = lang
            return True
        return False

# Instance globale
_translator = Translations('fr')

def get_translator():
    """Retourne l'instance du traducteur"""
    return _translator

def _(key, **kwargs):
    """Fonction de traduction rapide"""
    return _translator.get(key, **kwargs)

def set_language(lang):
    """Change la langue"""
    return _translator.set_language(lang)