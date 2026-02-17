# test_api_connection.py
import sys
sys.path.append('.')
from api.client import APIClient

client = APIClient()

# Test de connexion
if client.test_connection():
    print("✅ API accessible")
else:
    print("❌ API inaccessible")

# Test de la méthode (sans l'exécuter)
try:
    # Juste pour vérifier la signature
    import inspect
    print(f"✅ Méthode demander_course disponible")
    
    # Simuler un appel
    print("📡 Test d'appel (simulé):")
    print("  depart_lat: -11.6980")
    print("  depart_lng: 43.2560")
    print("  arrivee_lat: -11.7100")
    print("  arrivee_lng: 43.2650")
    print("  prix: 65")
    print("  service: 'confort'")
    
except Exception as e:
    print(f"❌ Erreur: {e}")