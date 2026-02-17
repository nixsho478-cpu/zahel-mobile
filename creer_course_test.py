# creer_course_test.py (version corrigée)
import requests
import json

print("🚗 CRÉATION D'UNE COURSE 'confort'")
print("=" * 50)

try:
    # Connexion client
    print("\n1. 🔐 CONNEXION CLIENT")
    response = requests.post(
        'http://localhost:5001/api/client/login',
        json={'telephone': '+26934011111', 'password': 'test123'},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    
    if not response.ok:
        print(f"❌ Échec: {response.text}")
        exit()
    
    client_data = response.json()
    token = client_data.get('token')
    print(f"✅ Token: {token}")
    
    # Créer course
    print("\n2. 📝 CRÉATION COURSE")
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    
    course_data = {
        'depart_lat': -11.698,
        'depart_lng': 43.256,
        'arrivee_lat': -11.710,
        'arrivee_lng': 43.265,
        'prix': 2200.0,
        'categorie': 'confort'  # Catégorie spécifique
    }
    
    response2 = requests.post(
        'http://localhost:5001/api/courses/demander',
        headers=headers,
        json=course_data,
        timeout=10
    )
    
    print(f"Status: {response2.status_code}")
    print(f"Réponse: {response2.text}")
    
    if response2.ok:
        course_info = response2.json()
        print(f"\n✅ SUCCÈS !")
        print(f"   Code: {course_info.get('course', {}).get('code')}")
        print(f"   Catégorie: 'confort'")
        
except Exception as e:
    print(f"❌ Erreur: {e}")