# zahel_mobile/api_client.py
import requests
import json

class ZAHELAPIClient:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.token = None
        self.user_type = None  # 'client' ou 'conducteur'
    
    # ========== CLIENT ==========
    
    def client_login(self, telephone, password):
        """Connexion client"""
        url = f"{self.base_url}/api/client/login"
        data = {"telephone": telephone, "password": password}
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get('token')
                self.user_type = 'client'
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def client_register(self, nom, telephone, password):
        """Inscription client"""
        url = f"{self.base_url}/api/client/register"
        data = {
            "nom": nom,
            "telephone": telephone,
            "password": password
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def demander_course(self, depart_lat, depart_lon, arrivee_lat, arrivee_lon, prix_convenu):
        """Demander une course"""
        url = f"{self.base_url}/api/courses/demander"
        headers = {"Authorization": self.token} if self.token else {}
        
        data = {
            "depart": {
                "lat": depart_lat,
                "lon": depart_lon,
                "adresse": "Position actuelle"
            },
            "arrivee": {
                "lat": arrivee_lat,
                "lon": arrivee_lon,
                "adresse": "Destination"
            },
            "prix_convenu": prix_convenu
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_courses_disponibles(self):
        """Récupérer les courses disponibles"""
        url = f"{self.base_url}/api/courses/disponibles"
        headers = {"Authorization": self.token} if self.token else {}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== CONDUCTEUR ==========
    
    def conducteur_login(self, immatricule, password):
        """Connexion conducteur"""
        url = f"{self.base_url}/api/conducteur/login"
        data = {"immatricule": immatricule, "password": password}
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get('token')
                self.user_type = 'conducteur'
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_conducteur_statistiques(self):
        """Récupérer les statistiques conducteur"""
        url = f"{self.base_url}/api/conducteur/statistiques"
        headers = {"Authorization": self.token} if self.token else {}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== UTILITAIRES ==========
    
    def test_connection(self):
        """Tester la connexion à l'API"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False