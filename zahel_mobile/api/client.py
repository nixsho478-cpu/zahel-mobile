# api/client.py - VERSION CORRECTE ET COMPLÈTE
import requests
import json

class APIClient:
    """Client API pour ZAHEL - Gère conducteur ET client"""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.token = None
        self.user_type = None  # 'client' ou 'conducteur'
        self.session = requests.Session()
        self.session.timeout = 10
        
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
            return {"success": False, "error": f"HTTP {response.status_code}"}
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
        """Accepter une course"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/courses/{course_code}/accepter",
                headers={"Authorization": self.token}
            )
            return response.json() if response.status_code == 200 else {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_course(self, course_code):
        """Commencer une course (changer statut: acceptee → en_cours)"""
        if not self.token:
            return {"success": False, "error": "Non authentifié"}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/courses/{course_code}/commencer",
                headers={"Authorization": self.token}
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
                headers={"Authorization": self.token}
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
                json={"telephone": telephone, "password": password}
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
        
    def accepter_course(self, code_course, token):
        """Accepter une course (pour conducteur)"""
        try:
            url = f"{self.base_url}/api/courses/{code_course}/accepter"
            headers = {
                'Authorization': str(token),
                'Content-Type': 'application/json'
            }
        
            print(f"🔍 Appel API: POST {url}")
            print(f"🔍 Token: {token}")
        
            response = self.session.post(url, headers=headers, timeout=10)
        
            print(f"🔍 Réponse API: {response.status_code}")
        
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API acceptation: {result}")
                return result
            else:
                print(f"❌ Erreur API: {response.status_code} - {response.text}")
                return {'success': False, 'error': f'Status {response.status_code}'}
            
        except Exception as e:
            print(f"❌ Exception API: {e}")
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