# api/client.py - VERSION CORRECTE ET COMPLÈTE
import requests
import json

class APIClient:
    """Client API pour ZAHEL - Gère conducteur ET client"""
    
    def __init__(self, base_url=None):
        # ⭐ UTILISER LA CONFIGURATION SI BASE_URL NON FOURNIE
        if base_url is None:
            from config.config import Config
            self.base_url = Config.API_BASE_URL
        else:
            self.base_url = base_url
            
        self.token = None
        self.user_type = None  # 'client' ou 'conducteur'
        self.session = requests.Session()
        self.session.timeout = 60
        
        print(f"🔌 API Client initialisé avec URL: {self.base_url}")
        
    # ========== MÉTHODES COMMUNES ==========
    
    def test_connection(self):
        """Tester la connexion à l'API"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def set_token(self, token, user_type):
        """Définir le token d'authentification"""
        self.token = token
        self.user_type = user_type
        # Mettre à jour les headers de session
        if self.token:
            self.session.headers.update({'Authorization': self.token})
        return True
    
    def get_user_type(self):
        """Obtenir le type d'utilisateur"""
        return self.user_type
    
    # ========== MÉTHODES CONDUCTEUR ==========
    
    def login(self, immatricule, password):
        """Connexion conducteur"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/conducteur/login",
                json={"immatricule": immatricule, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('token', immatricule)
                    self.user_type = 'conducteur'
                return data
            else:
                # ⭐⭐⭐ EXTRAIRE LE MESSAGE D'ERREUR DU JSON ⭐⭐⭐
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', f"HTTP {response.status_code}")
                except:
                    error_msg = f"HTTP {response.status_code}"
                return {"success": False, "error": error_msg}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_conducteur_info(self):
        """Obtenir les infos du conducteur"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/conducteur/statistiques",
                headers={"Authorization": self.token}
            )
            return response.json() if response.status_code == 200 else {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_available_courses(self):
        """Obtenir les courses disponibles"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/courses/disponibles",
                headers={"Authorization": self.token}
            )
            return response.json() if response.status_code == 200 else {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def accept_course(self, course_code):
        """Accepter une course et retourner les coordonnées"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
    
        try:
            response = self.session.post(
                f"{self.base_url}/api/courses/{course_code}/accepter",
                headers={"Authorization": self.token}
            )
        
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_course(self, course_code):
        """Commencer une course (changer statut: acceptee → en_cours)"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/courses/{course_code}/commencer",
                headers={"Authorization": self.token},
                timeout=30
            )
            return response.json() if response.status_code == 200 else {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def finish_course(self, course_code):
        """Terminer une course (changer statut: en_cours → terminee)"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/courses/{course_code}/terminer",
                headers={"Authorization": self.token},
                timeout=30
            )
            return response.json() if response.status_code == 200 else {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def toggle_status(self, disponible):
        """Changer le statut disponible/indisponible"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/conducteur/toggle_status",
                headers={"Authorization": self.token},
                json={"disponible": disponible}
            )
            return response.json() if response.status_code == 200 else {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== MÉTHODES CLIENT ==========
    
    def client_login(self, telephone, password):
        """Connexion client"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/client/login",
                json={"telephone": telephone, "password": password},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('token', telephone)
                    self.user_type = 'client'
                return data
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def client_register(self, nom, telephone, password):
        """Inscription client - VERSION CORRIGÉE"""
        data = {
            'nom': nom,
            'telephone': telephone,
            'password': password
        }
    
        try:
            response = self.session.post(
                f"{self.base_url}/api/client/register",
                json=data
            )
            # ✅ CORRECTION : Accepter 200 ET 201
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ⭐⭐ MÉTHODE CORRIGÉE ICI ⭐⭐
    def demander_course(self, depart_lat, depart_lng, arrivee_lat, arrivee_lng, prix, service="standard", conducteur_demande=None, amende_incluse=None):
        """Demander une course (cote client) - VERSION AVEC AMENDE"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            data = {
                'depart_lat': depart_lat,
                'depart_lng': depart_lng,
                'arrivee_lat': arrivee_lat,
                'arrivee_lng': arrivee_lng,
                'prix': prix,
                'categorie': service 
            }
        
            if conducteur_demande:
                data['conducteur_demande'] = conducteur_demande
        
            if amende_incluse:
                data['amende_incluse'] = amende_incluse  # <-- NOUVEAU
        
            response = self.session.post(
                f"{self.base_url}/api/courses/demander",
                headers={'Authorization': self.token},
                json=data
            )

            # Accepter 200 OU 201 comme succès
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    'success': False, 
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_client_courses(self):
        """Obtenir les courses du client"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/client/courses",
                headers={"Authorization": self.token}
            )
            return response.json() if response.status_code == 200 else {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cancel_course(self, course_code):
        """Annuler une course (côté client)"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
    
        try:
            # ✅ IMPORTANT : AJOUTER LE HEADER Content-Type
            headers = {
                "Authorization": self.token,
                "Content-Type": "application/json"  # ← CRITIQUE !
            }
        
            response = self.session.post(
                f"{self.base_url}/api/courses/{course_code}/annuler",
                json={"raison": "client_cancel"},  # ← Envoyer un body JSON
                headers=headers
            )
        
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== UTILITAIRES ==========
    
    def get_headers(self):
        """Obtenir les headers avec token"""
        if self.token:
            return {"Authorization": self.token}
        return {}

    def _get_headers(self):
        """Obtenir les headers avec token"""
        if self.token:
            return {"Authorization": self.token}
        return {}

    def get_available_drivers(self, lat=None, lng=None, radius=5):
        """Obtenir les conducteurs disponibles près d'une position"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            params = {}
            if lat and lng:
                params = {'lat': lat, 'lng': lng, 'radius': radius}
        
            response = self.session.get(
                f"{self.base_url}/api/conducteurs/disponibles",
                headers={'Authorization': self.token},
                params=params
            )
        
            if response.status_code == 200:
                return response.json()
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def verifier_amendes_client(self):
        """Vérifier si le client a des amendes impayées - VERSION CORRIGÉE"""
        print(f"\n🔍 DEBUG verifier_amendes_client()")
        print(f"   Token: {self.token}")
        print(f"   User type: {self.user_type}")
    
        if not self.token:
            print("❌ Pas de token")
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            print(f"🔍 Appel API: {self.base_url}/api/client/amendes")
            response = self.session.get(
                f"{self.base_url}/api/client/amendes",
                headers={'Authorization': self.token},
                timeout=5
            )
        
            print(f"🔍 Réponse status: {response.status_code}")
        
            if response.status_code == 200:
                result = response.json()
                print(f"🔍 Réponse JSON reçue")
            
                # Vérifier la structure de la réponse
                if result.get('success'):
                    amendes = result.get('amendes', [])
                    count_impayees = result.get('count_impayees', 0)
                    total_impayees = result.get('total_impayees', 0)
                
                    print(f"🔍 Amendes trouvées: {len(amendes)}")
                    print(f"🔍 Amendes impayées: {count_impayees}")
                    print(f"🔍 Total impayé: {total_impayees}")
                
                    # Filtrer les amendes impayées
                    amendes_impayees = [a for a in amendes if a.get('statut') in ['en_attente', 'impayee']]
                
                    has_amendes = len(amendes_impayees) > 0
                
                    return {
                        'success': True,
                        'amendes': amendes_impayees,
                        'count_impayees': len(amendes_impayees),
                        'total_impayees': total_impayees,
                        'has_amendes': has_amendes  # ← AJOUT IMPORTANT !
                    }
                else:
                    print(f"❌ API error: {result.get('error')}")
                    return result
                
            elif response.status_code == 404:
                print("ℹ️ Route amendes non trouvée (404)")
                return {'success': True, 'amendes': [], 'has_amendes': False}
            else:
                error_text = response.text[:200] if response.text else 'No response text'
                print(f"❌ HTTP error {response.status_code}: {error_text}")
                return {
                    'success': False, 
                    'error': f'HTTP {response.status_code}',
                    'details': error_text
                }
            
        except Exception as e:
            print(f"❌ Exception vérification amendes: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e), 'amendes': [], 'has_amendes': False}   

    def get_available_courses_with_amendes(self):
        """Récupère les courses disponibles avec info amendes"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            response = self.session.get(
                f"{self.base_url}/api/courses/disponibles",
                headers={'Authorization': self.token},
                timeout=10
            )
        
            if response.status_code == 200:
                result = response.json()
            
                # DEBUG: Afficher les infos amendes
                if result.get('success') and result.get('courses'):
                    for course in result['courses']:
                        if course.get('amende_incluse'):
                            print(f"📋 Course {course['code']} a une amende: {course['montant_amende']} KMF")
            
                return result
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}        

    def get_course_status(self, course_code):
        """
        Récupère le statut d'une course depuis l'API
        """
        if not self.base_url or not self.token:
            print("⚠️ API non configurée pour get_course_status")
            return {'success': False, 'error': 'API non configurée'}
        
        try:
            url = f"{self.base_url}/api/courses/{course_code}/statut"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {self.token}"
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ Erreur API get_course_status: {response.status_code}")
                return {'success': False, 'error': f"Erreur {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur connexion get_course_status: {e}")
            return {'success': False, 'error': 'Connexion impossible'}
        except Exception as e:
            print(f"⚠️ Erreur inattendue get_course_status: {e}")
            return {'success': False, 'error': 'Erreur inattendue'}
        
    def get_notifications_conducteur(self, token):
        """Récupérer les notifications du conducteur"""
        try:
            response = requests.get(
                f"{self.base_url}/api/conducteur/notifications/nouvelles",
                headers={'Authorization': token},
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"❌ Erreur récupération notifications: {e}")
            return {'success': False, 'notifications': [], 'error': str(e)}
    
    def get_notifications_non_lues(self, token):
        """Récupérer le nombre de notifications non lues"""
        try:
            response = requests.get(
                f"{self.base_url}/api/conducteur/notifications/non_lues",
                headers={'Authorization': token},
                timeout=5
            )
            return response.json()
        except Exception as e:
            print(f"⚠️ Erreur notifications non lues: {e}")
            return {'success': True, 'count': 0, 'has_notifications': False}
    
    def marquer_notification_lue(self, token, course_code):
        """Marquer une notification comme lue"""
        try:
            response = requests.post(
                f"{self.base_url}/api/conducteur/notifications/marquer_lue",
                headers={'Authorization': token},
                json={'course_code': course_code},
                timeout=5
            )
            return response.json()
        except Exception as e:
            print(f"⚠️ Erreur marquer notification lue: {e}")
            return {'success': False, 'error': str(e)}
        
    def _request(self, method, endpoint, data=None):
        """Méthode interne pour faire les requêtes HTTP"""
        import requests
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': self.token if self.token else '',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return {'success': False, 'error': f'Méthode {method} non supportée'}
            
            # DEBUG
            print(f"🔍 API {method} {url}")
            print(f"🔍 Headers: {headers}")
            print(f"🔍 Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'details': response.text[:200]
                }
                
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connexion API impossible'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_luxe_timeout(self, course_code):
        """Vérifier le timeout d'une course Luxe"""
        try:
            response = self._request('GET', f'/api/courses/{course_code}/check_luxe')
            return response
        except Exception as e:
            print(f"❌ Erreur check_luxe_timeout: {e}")
            return {'success': False, 'error': str(e)}
    
    def switch_to_confort(self, course_code):
        """Changer une course de Luxe à Confort"""
        try:
            response = self._request('POST', f'/api/courses/{course_code}/switch_to_confort')
            return response
        except Exception as e:
            print(f"❌ Erreur switch_to_confort: {e}")
            return {'success': False, 'error': str(e)}

    def _public_request(self, method, endpoint):
        """Méthode pour les routes publiques (sans token)"""
        import requests
    
        url = f"{self.base_url}{endpoint}"
    
        try:
            if method == 'GET':
                response = requests.get(url, timeout=10)
            else:
                return {'success': False, 'error': f'Méthode {method} non supportée pour les requêtes publiques'}
        
            print(f"🔍 API PUBLIC {method} {url}")
            print(f"🔍 Status: {response.status_code}")
        
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'details': response.text[:200]
                }
            
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connexion API impossible'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check_luxe_timeout(self, course_code):
        """Vérifier le timeout d'une course Luxe"""
        return self._public_request('GET', f'/api/courses/{course_code}/check_luxe')   

    def reset_luxe_timer(self, course_code):
        """Réinitialiser le timer luxe d'une course"""
        try:
            # ⭐⭐ IMPORTANT : Route publique, pas besoin de token
            url = f"{self.base_url}/api/courses/{course_code}/reset_luxe_timer"
            response = requests.post(url, timeout=10)
        
            print(f"🔍 API POST {url}")
            print(f"🔍 Status: {response.status_code}")
        
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'details': response.text[:200]
                }
            
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connexion API impossible'}
        except Exception as e:
            return {'success': False, 'error': str(e)}     

    def get_client_adresses(self):
        """Récupérer les adresses fréquentes du client"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
    
        try:
            response = self.session.get(
                f"{self.base_url}/api/client/adresses",
                headers={"Authorization": self.token}
            )
            return response.json() if response.status_code == 200 else {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_client_adresse(self, nom, adresse, latitude=None, longitude=None, type_adresse='personnel'):
        """Ajouter une adresse fréquente"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
    
        data = {
            'nom': nom,
            'adresse': adresse,
            'latitude': latitude,
            'longitude': longitude,
            'type': type_adresse
        }
    
        try:
            response = self.session.post(
                f"{self.base_url}/api/client/adresses",
                headers={"Authorization": self.token, "Content-Type": "application/json"},
                json=data
            )
            return response.json() if response.status_code == 201 else {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_client_adresse(self, adresse_id):
        """Supprimer une adresse fréquente"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
    
        try:
            response = self.session.delete(
                f"{self.base_url}/api/client/adresses/{adresse_id}",
                headers={"Authorization": self.token}
            )
            return response.json() if response.status_code == 200 else {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def change_password(self, old_password, new_password):
        """Changer le mot de passe du client"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
    
        data = {
            'old_password': old_password,
            'new_password': new_password
        }
    
        try:
            response = self.session.post(
                f"{self.base_url}/api/client/change_password",
                headers={"Authorization": self.token, "Content-Type": "application/json"},
                json=data
            )
            return response.json() if response.status_code == 200 else {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def register_driver(self, driver_data):
        """Inscription d'un nouveau conducteur - Version HYBRIDE WHATSAPP"""
        try:
            print(f"📤 API: Inscription conducteur {driver_data.get('telephone')} - {driver_data.get('categorie')}")
         
            response = requests.post(
                f"{self.base_url}/api/conducteurs/inscription",
                json=driver_data,
                timeout=10
            )
        
            if response.status_code in [200, 201]:
                result = response.json()
                conducteur = result.get('conducteur', {})
                verification = conducteur.get('verification_requise', False)
            
                if verification:
                    print(f"✅ API: Inscription SOUMISE - {conducteur.get('immatricule')} - Vérification WhatsApp requise")
                else:
                    print(f"✅ API: Inscription RÉUSSIE - {conducteur.get('immatricule')} - Activation immédiate")
                
                return result
            else:
                print(f"❌ API: Erreur {response.status_code}")
                try:
                    error_data = response.json()
                    return {'success': False, 'error': error_data.get('error', 'Erreur inconnue')}
                except:
                    return {'success': False, 'error': f'Erreur {response.status_code}'}
                
        except requests.exceptions.ConnectionError:
            print("❌ API: Erreur de connexion - Serveur indisponible")
            return {'success': False, 'error': 'Serveur indisponible'}
        except Exception as e:
            print(f"❌ API: Exception {e}")
            return {'success': False, 'error': str(e)}

    def get_driver_stats(self, lat, lng, radius=5, category=None):
        """Récupérer les statistiques des conducteurs disponibles"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            url = f"{self.base_url}/api/conducteurs/stats"
            params = {
                'lat': lat,
                'lng': lng,
                'radius': radius
            }
            if category:
                params['category'] = category
        
            response = self.session.get(
                url,
                headers={'Authorization': self.token},
                params=params,
                timeout=5
            )
        
            if response.status_code == 200:
                return response.json()
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def marquer_toutes_notifications_lues(self):
        """Marquer toutes les notifications comme lues en UN SEUL appel"""
        if not self.token: 
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            response = self.session.post(
                f"{self.base_url}/api/conducteur/notifications/marquer_toutes_lues",
                headers=self._get_headers()
            )
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_amendes_a_collecter(self):
        """Récupérer les amendes à collecter pour le conducteur connecté"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            response = self.session.get(
                f"{self.base_url}/api/conducteur/amendes_a_collecter",
                headers=self._get_headers()
            )
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def confirmer_collecte_amende(self, amende_chauffeur_id):
        """Confirmer qu'une amende a été versée à l'agence"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            response = self.session.post(
                f"{self.base_url}/api/conducteur/amendes/confirmer_collecte",
                headers=self._get_headers(),
                json={'amende_chauffeur_id': amende_chauffeur_id}
            )
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_amendes_stats_conducteur(self):
        """Récupérer les statistiques des amendes pour le conducteur"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            response = self.session.get(
                f"{self.base_url}/api/conducteur/amendes/statistiques",
                headers=self._get_headers()
            )
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_conducteur_historique(self):
        """Récupérer l'historique mensuel du conducteur"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            print(f"📡 Appel API historique: {self.base_url}/api/conducteur/historique")
            response = self.session.get(
                f"{self.base_url}/api/conducteur/historique",
                headers=self._get_headers(),
                timeout=10
            )
            print(f"📡 Status: {response.status_code}")
        
            if response.status_code == 200:
                return response.json()
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            print(f"❌ Erreur historique: {e}")
            return {'success': False, 'error': str(e)}

    def renouveler_abonnement(self):
        """Préparer le renouvellement d'abonnement"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            response = self.session.post(
                f"{self.base_url}/api/conducteur/renouveler",
                headers=self._get_headers()
            )
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def verifier_statut_conducteur(self):
        """Vérifier le statut du conducteur et libérer si nécessaire"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            response = self.session.get(
                f"{self.base_url}/api/conducteur/verifier_statut",
                headers=self._get_headers(),
                timeout=5
            )
        
            if response.status_code == 200:
                return response.json()
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def send_location_from_intent(self, lat, lng, source='whatsapp'):
        """Envoyer une localisation reçue d'un intent"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}
    
        try:
            response = self.session.post(
                f"{self.base_url}/api/client/location",
                headers={'Authorization': self.token},
                json={'lat': lat, 'lng': lng, 'source': source},
                timeout=5
            )
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========== MAPBOX MÉTHODES ==========
    
    def geocode_address(self, address):
        """
        Convertir une adresse en coordonnées avec Mapbox
        Exemple: geocode_address("Moroni Centre")
        Retourne: {'success': True, 'latitude': -11.698, 'longitude': 43.256, 'place_name': '...'}
        """
        try:
            from urllib.parse import quote
            import requests
            
            # Importer la configuration Mapbox
            import sys
            import os.path as osp
            sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
            from config.mapbox_config import MapboxConfig
            
            # Encoder l'adresse pour l'URL
            encoded_address = quote(address)
            url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded_address}.json"
            params = {
                'access_token': MapboxConfig.ACCESS_TOKEN,
                'limit': 1,
                'country': 'km'  # Limiter aux Comores
            }
            
            print(f"📍 Géocodage: {address}")
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('features'):
                feature = data['features'][0]
                coords = feature['geometry']['coordinates']
                return {
                    'success': True,
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'place_name': feature['place_name'],
                    'address': feature.get('text', address)
                }
            return {'success': False, 'error': 'Adresse non trouvée'}
            
        except Exception as e:
            print(f"❌ Erreur geocode_address: {e}")
            return {'success': False, 'error': str(e)}
    
    def reverse_geocode(self, lat, lng):
        """
        Convertir des coordonnées en adresse avec Nominatim (gratuit + cache)
        Exemple: reverse_geocode(-11.698, 43.256)
        Retourne: {'success': True, 'address': 'Moroni, Comores'}
        """
        try:
            import requests
        
            # ⭐⭐⭐ UTILISER LE PROXY NOMINATIM (PORT 5002) ⭐⭐⭐
            url = f"http://zahel-comores.com:5002/reverse"
            params = {
                'lat': lat,
                'lng': lng
            }
        
            print(f"📍 Reverse géocodage (Nominatim): ({lat:.6f}, {lng:.6f})")
            response = requests.get(url, params=params, timeout=10)
        
            if response.status_code == 200:
                data = response.json()
                if data.get('display_name'):
                    # Prendre la première partie de l'adresse (plus lisible)
                    address_parts = data['display_name'].split(',')
                    short_address = address_parts[0].strip() if address_parts else data['display_name']
                
                    return {
                        'success': True,
                        'address': short_address,
                        'full_address': data['display_name'],
                        'coordinates': (lat, lng)
                    }
        
            # Fallback: utiliser Mapbox si Nominatim échoue
            print(f"⚠️ Nominatim échoué, fallback Mapbox")
            import sys
            import os.path as osp
            sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
            from config.mapbox_config import MapboxConfig
        
            url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lng},{lat}.json"
            params = {
                'access_token': MapboxConfig.ACCESS_TOKEN,
                'limit': 1
            }
        
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
        
            if data.get('features'):
                feature = data['features'][0]
                return {
                    'success': True,
                    'address': feature['place_name'],
                    'coordinates': (lat, lng)
                }
        
            # Fallback ultime
            return {
                'success': True, 
                'address': f"{lat:.4f}, {lng:.4f}",
                'coordinates': (lat, lng)
            }
        
        except Exception as e:
            print(f"❌ Erreur reverse_geocode: {e}")
            return {
                'success': True,  # On retourne quand même quelque chose
                'address': f"{lat:.4f}, {lng:.4f}",
                'coordinates': (lat, lng)
            }
    
    def get_route(self, start_lat, start_lng, end_lat, end_lng):
        """Calculer un itinéraire avec Mapbox Directions API"""
        try:
            import requests
            from config.mapbox_config import MapboxConfig
        
            # Format pour Mapbox: lng,lat
            start_coords = f"{start_lng},{start_lat}"
            end_coords = f"{end_lng},{end_lat}"
        
            url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_coords};{end_coords}"
            params = {
                'access_token': MapboxConfig.ACCESS_TOKEN,
                'geometries': 'geojson',
                'overview': 'full',
                'steps': 'true'
            }
        
            print(f"🗺️ Appel Directions API: {start_lat},{start_lng} → {end_lat},{end_lng}")
        
            # ⭐ AJOUTER UN TIMEOUT ET GÉRER LES ERREURS SSL
            response = requests.get(url, params=params, timeout=15, verify=True)
            print(f"🗺️ Status: {response.status_code}")
        
            if response.status_code == 200:
                data = response.json()
                if data.get('routes'):
                    route = data['routes'][0]
                    return {
                        'success': True,
                        'distance_km': round(route['distance'] / 1000, 1),
                        'duration_min': round(route['duration'] / 60, 1),
                        'geometry': route['geometry'],
                        'instructions': [step['maneuver']['instruction'] for step in route['legs'][0]['steps']]
                    }
            elif response.status_code == 422:
                print("⚠️ Erreur 422: Coordonnées invalides ou trop proches")
            elif response.status_code == 429:
                print("⚠️ Erreur 429: Trop de requêtes, attendez un moment")
            else:
                print(f"⚠️ Erreur HTTP {response.status_code}: {response.text[:200]}")
        
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        
        except requests.exceptions.SSLError as e:
            print(f"⚠️ Erreur SSL (temporaire): {e}")
            print("🔄 Utilisation du fallback local (ligne droite)")
            return {'success': False, 'error': 'SSL Error - fallback utilisé'}
        except requests.exceptions.Timeout:
            print("⚠️ Timeout API Mapbox")
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            print(f"❌ Erreur get_route: {e}")
            return {'success': False, 'error': str(e)}

    def update_driver_position(self, lat, lng):
        """Mettre à jour la position du conducteur avec retry"""
        if not self.token:
            return {'success': False, 'error': 'Non authentifié'}

        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/conducteur/position",
                    headers={'Authorization': self.token},
                    json={'latitude': lat, 'longitude': lng},
                    timeout=8
                )
                print(f"📍 Position envoyée: ({lat:.6f}, {lng:.6f}) - Status: {response.status_code}")
                return response.json() if response.status_code == 200 else {'success': False}
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"⚠️ Échec envoi position après {max_retries} tentatives: {e}")
                    return {'success': False, 'error': str(e)}
                else:
                    import time
                    time.sleep(1)  # Attendre 1s avant de réessayer