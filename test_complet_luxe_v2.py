# test_complet_luxe_v2.py
import requests
import json
import time

base_url = "http://localhost:5001"

print("=== TEST COMPLET FONCTIONNALITÉ LUXE ===")
print("=========================================")

# 1. Connexion du client pour obtenir un token
print("\n1. 🔐 CONNEXION CLIENT POUR TOKEN")
login_data = {
    "telephone": "+26934011111",  # Client test existant
    "password": "test123"
}

response = requests.post(
    f"{base_url}/api/client/login",
    json=login_data,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
login_result = response.json()
print(f"Réponse: {json.dumps(login_result, indent=2)}")

if response.status_code != 200:
    print("❌ Échec de connexion, test avec token vide")
    token = None
    client_id = 1  # ID par défaut
else:
    token = login_result.get('token')
    client_data = login_result.get('client', {})
    client_id = client_data.get('id', 1)
    print(f"✅ Token obtenu: {token[:20]}...")
    print(f"✅ Client ID: {client_id}")

# 2. Créer une course LUXE
print(f"\n2. 🚗 CRÉATION D'UNE COURSE LUXE")
data = {
    "client_id": client_id,
    "depart_lat": -11.698,
    "depart_lng": 43.256,
    "arrivee_lat": -11.704,
    "arrivee_lng": 43.261,
    "prix": 5000,
    "categorie": "luxe"  # TRÈS IMPORTANT
}

headers = {"Content-Type": "application/json"}
if token:
    headers["Authorization"] = f"Bearer {token}"

response = requests.post(
    f"{base_url}/api/courses/demander",
    json=data,
    headers=headers
)

print(f"Status: {response.status_code}")
result = response.json()
print(f"Réponse: {json.dumps(result, indent=2)}")

if response.status_code != 200:
    print("❌ Échec de création de course")
    # Essayons sans token pour debug
    print("\n⚠️  Essai sans token...")
    response = requests.post(
        f"{base_url}/api/courses/demander",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status sans token: {response.status_code}")
    print(f"Réponse: {response.text[:200]}")
    exit()

course_code = result.get('course_code')
print(f"\n✅ Course créée: {course_code}")

# 3. Tester immédiatement check_luxe
print(f"\n3. 🔍 TEST CHECK_LUXE IMMÉDIAT POUR {course_code}")
response = requests.get(f"{base_url}/api/courses/{course_code}/check_luxe")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Réponse: {json.dumps(result, indent=2)}")

if result.get('is_luxe'):
    print("✅ Course correctement identifiée comme LUXE")
    print(f"   Temps restant: {result.get('temps_restant')} secondes")
else:
    print(f"❌ Problème: {result.get('message')}")

# 4. Vérifier la course dans la base de données
print(f"\n4. 📊 VÉRIFICATION BASE DE DONNÉES POUR {course_code}")
response = requests.get(f"{base_url}/api/debug/all_courses")
if response.status_code == 200:
    all_courses = response.json().get('courses', [])
    for course in all_courses:
        if course.get('code_unique') == course_code:
            print(f"✅ Course trouvée dans la base:")
            print(f"   Catégorie: {course.get('categorie_demande')}")
            print(f"   Statut: {course.get('statut')}")
            print(f"   Timer luxe démarré: {course.get('timer_luxe_demarre_le')}")
            break

# 5. Tester après une courte attente
print(f"\n5. ⏱️  TEST APRÈS ATTENTE (5 secondes)")
time.sleep(5)

response = requests.get(f"{base_url}/api/courses/{course_code}/check_luxe")
result = response.json()
if result.get('is_luxe'):
    print(f"✅ Temps restant après attente: {result.get('temps_restant')} secondes")
else:
    print(f"❌ {result.get('message')}")

print("\n=========================================")
print("✅ TEST TERMINÉ")