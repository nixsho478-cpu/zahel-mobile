# test_simple_apres_corrections.py
import requests
import time

print("🧪 TEST SIMPLIFIÉ APRÈS CORRECTIONS")
print("="*50)

# Configuration
TOKEN_CLIENT = "+26934011111"
BASE_URL = "http://localhost:5001"

print("1. Création d'une course...")
response = requests.post(
    f"{BASE_URL}/api/courses/demander",
    headers={"Authorization": TOKEN_CLIENT},
    json={
        "depart_lat": -11.698,
        "depart_lng": 43.256,
        "arrivee_lat": -11.704,
        "arrivee_lng": 43.261,
        "prix": 1000
    }
)

if response.status_code == 201:
    course_code = response.json()['course']['code']
    print(f"✅ Course créée: {course_code}")
    
    # Attendre 2 secondes pour être sûr
    time.sleep(2)
    
    print(f"\n2. Annulation de la course {course_code}...")
    response2 = requests.post(
        f"{BASE_URL}/api/courses/{course_code}/annuler",
        headers={"Authorization": TOKEN_CLIENT},
        json={"raison": "test_simple"}
    )
    
    print(f"   Status: {response2.status_code}")
    
    if response2.status_code == 200:
        result = response2.json()
        print(f"✅ SUCCÈS! Annulation fonctionne!")
        print(f"   Résultat: {result}")
        
        # Sauvegarder pour référence
        with open('derniere_annulation_reussie.txt', 'w') as f:
            f.write(f"Course: {course_code}\n")
            f.write(f"Résultat: {str(result)[:200]}\n")
            
    elif response2.status_code == 500:
        print("❌ Erreur 500 - Regardez le serveur Flask")
        print(f"   Message: {response2.text[:200]}")
        
    else:
        print(f"⚠️ Autre erreur: {response2.text[:200]}")
        
else:
    print(f"❌ Erreur création: {response.status_code}")
    print(f"   Message: {response.text[:200]}")