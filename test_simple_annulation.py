# test_simple_annulation.py
import requests

print("🧪 TEST SIMPLE D'ANNULATION")
print("="*50)

# 1. Créer une course
token_client = "+26934011111"  # SANS "Bearer "

course_data = {
    "depart_lat": -11.698,
    "depart_lng": 43.256,
    "arrivee_lat": -11.704,
    "arrivee_lng": 43.261,
    "prix": 1000
}

print("📝 Création d'une course...")
response = requests.post(
    "http://localhost:5001/api/courses/demander",
    headers={"Authorization": token_client},
    json=course_data,
    timeout=10
)

if response.status_code == 201:
    course_code = response.json()['course']['code']
    print(f"✅ Course créée: {course_code}")
    
    # 2. Annuler immédiatement
    print("\n❌ Annulation immédiate...")
    response = requests.post(
        f"http://localhost:5001/api/courses/{course_code}/annuler",
        headers={"Authorization": token_client},
        json={"raison": "test_annulation"}
    )
    
    if response.status_code == 200:
        print("✅ Annulation réussie!")
        print(f"Résultat: {response.json()}")
    else:
        print(f"❌ Erreur annulation: {response.status_code}")
        print(f"Détails: {response.text[:200]}")
        
else:
    print(f"❌ Erreur création: {response.status_code}")
    print(f"Détails: {response.text[:200]}")