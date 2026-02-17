# zahel_mobile/api/client.py
import requests
import json

class APIClient:
    def __init__(self):
        self.token = None
        self.base_url = "http://localhost:5001"
        print(f"✅ APIClient initialisé avec base_url: {self.base_url}")
    
    def login(self, immatricule, password):
        """Connexion à l'API ZAHEL"""
        try:
            print(f"🔐 Tentative de connexion API: {immatricule}")
            response = requests.post(
                f"{self.base_url}/api/conducteurs/login",
                json={
                    'immatricule': immatricule,
                    'password': password
                },
                timeout=10
            )
            print(f"📥 Réponse login: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('token')
                    print(f"✅ Connexion API réussie, token: {self.token[:20]}...")
                return data
            else:
                print(f"❌ Erreur login HTTP: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"❌ Exception login: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_conducteur_info(self):
        """Récupère les infos du conducteur"""
        try:
            if not self.token:
                return {'success': False, 'error': 'Non connecté'}
            
            print(f"📡 Appel API get_conducteur_info avec token: {self.token[:20]}...")
            response = requests.get(
                f"{self.base_url}/api/conducteurs/me",
                headers={'Authorization': self.token},
                timeout=10
            )
            print(f"📥 Réponse conducteur: Status {response.status_code}")
            return response.json()
            
        except Exception as e:
            print(f"❌ Exception get_conducteur_info: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_available_courses(self):
        """Récupère les courses disponibles"""
        try:
            if not self.token:
                return {'success': False, 'error': 'Non connecté'}
            
            print(f"📡 Appel API get_available_courses avec token: {self.token[:20]}...")
            response = requests.get(
                f"{self.base_url}/api/courses/disponibles",
                headers={'Authorization': self.token},
                timeout=10
            )
            print(f"📥 Réponse courses: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 API retourne: {data.get('count', 0)} courses")
                return data
            else:
                print(f"❌ Erreur HTTP courses: {response.status_code}")
                return {
                    'success': False, 
                    'error': f'HTTP {response.status_code}',
                    'count': 0,
                    'courses': []
                }
                
        except Exception as e:
            print(f"❌ Exception get_available_courses: {e}")
            return {
                'success': False, 
                'error': str(e),
                'count': 0,
                'courses': []
            }
    
    def accept_course(self, course_code):
        """Accepte une course"""
        try:
            print(f"✅ Acceptation course: {course_code}")
            response = requests.post(
                f"{self.base_url}/api/courses/{course_code}/accepter",
                headers={'Authorization': self.token},
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"❌ Exception accept_course: {e}")
            return {'success': False, 'error': str(e)}

    def start_course(self, course_code):
        """Démarrer une course"""
        try:
            print(f"🚗 Démarrage course API: {course_code}")
            response = requests.post(
                f"{self.base_url}/api/courses/{course_code}/commencer",
                headers={'Authorization': self.token},
                timeout=10
            )
            print(f"📡 Réponse démarrage: Status {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"❌ Erreur start_course: {e}")
            return {'success': False, 'error': str(e)}
    
    def toggle_status(self, disponible):
        """Change le statut du conducteur"""
        try:
            response = requests.post(
                f"{self.base_url}/api/conducteurs/toggle_status",
                headers={'Authorization': self.token},
                json={'disponible': disponible},
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"❌ Exception toggle_status: {e}")
            return {'success': False, 'error': str(e)}
   