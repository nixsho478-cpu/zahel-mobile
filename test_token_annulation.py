# test_token_annulation.py
import requests

print("🔍 TEST TOKEN POUR ANNULATION")
print("="*50)

token = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"
course_code = "ZAHEL-ZBA2671"  # La dernière course créée

print(f"Token utilisé: {token[:20]}...")
print(f"Course: {course_code}")

# Test 1: Vérifier que le token marche pour GET /
print("\n1. 🔐 Test GET / avec ce token:")
try:
    r = requests.get("http://localhost:5001", 
                    headers={"Authorization": token},
                    timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Réponse: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 2: Essayer d'annuler
print("\n2. 🚫 Test annulation:")
annulation_data = {"raison": "test"}
try:
    r = requests.post(f"http://localhost:5001/api/courses/{course_code}/annuler",
                     headers={"Authorization": token},
                     json=annulation_data,
                     timeout=10)
    print(f"   Status: {r.status_code}")
    print(f"   Réponse: {r.text[:200]}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "="*50)