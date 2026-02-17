# test_complet_luxe.py
import requests
import json
import time

base_url = "http://localhost:5001"

print("=== TEST COMPLET FONCTIONNALITÉ LUXE ===")
print("=========================================")

# 1. Créer une course LUXE
print("\n1. 🚗 CRÉATION D'UNE COURSE LUXE")
data = {
    "client_id": 1,
    "depart_lat": -11.698,
    "depart_lng": 43.256,
    "arrivee_lat": -11.704,
    "arrivee_lng": 43.261,
    "prix": 5000,
    "categorie": "luxe"  # TRÈS IMPORTANT
}

response = requests.post(
    f"{base_url}/api/courses/demander",
    json=data,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
result = response.json()
print(f"Réponse: {json.dumps(result, indent=2)}")

if response.status_code != 200:
    print("❌ Échec de création de course")
    exit()

course_code = result.get('course_code')
print(f"\n✅ Course créée: {course_code}")

# 2. Tester immédiatement check_luxe
print(f"\n2. 🔍 TEST CHECK_LUXE IMMÉDIAT POUR {course_code}")
response = requests.get(f"{base_url}/api/courses/{course_code}/check_luxe")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Réponse: {json.dumps(result, indent=2)}")

if result.get('is_luxe'):
    print("✅ Course correctement identifiée comme LUXE")
    print(f"   Temps restant: {result.get('temps_restant')} secondes")
else:
    print(f"❌ Problème: {result.get('message')}")

# 3. Attendre 10 secondes et re-tester
print(f"\n3. ⏱️  TEST APRÈS ATTENTE (10 secondes)")
time.sleep(10)

response = requests.get(f"{base_url}/api/courses/{course_code}/check_luxe")
result = response.json()
print(f"Temps restant après attente: {result.get('temps_restant', 'N/A')} secondes")

# 4. Tester le switch_to_confort (optionnel)
print(f"\n4. 🔄 TEST SWITCH_TO_CONFORT POUR {course_code}")
response = requests.post(
    f"{base_url}/api/courses/{course_code}/switch_to_confort",
    json={},
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Réponse: {json.dumps(result, indent=2)}")
    print(f"✅ Prix réduit de {result.get('reduction_percent', 0)}%")
else:
    print(f"❌ Échec: {response.text}")

print("\n=========================================")
print("✅ TEST TERMINÉ")