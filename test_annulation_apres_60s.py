# test_annulation_apres_60s.py
import requests
import time
import json

print("⏰ TEST ANNULEEATION APRÈS 60 SECONDES")
print("="*50)

TOKEN_CLIENT = "+26934011111"
BASE_URL = "http://localhost:5001"

# 1. Créer une course
print("1. Création d'une course...")
response = requests.post(
    f"{BASE_URL}/api/courses/demander",
    headers={"Authorization": TOKEN_CLIENT},
    json={
        "depart_lat": -11.698,
        "depart_lng": 43.256,
        "arrivee_lat": -11.704,
        "arrivee_lng": 43.261,
        "prix": 1500
    }
)

if response.status_code != 201:
    print(f"❌ Erreur création: {response.text}")
    exit()

course = response.json()['course']
COURSE_CODE = course['code']
print(f"✅ Course créée: {COURSE_CODE}")
print(f"   Statut: {course['statut']}")
print(f"   Conducteur attribué: {'✅ Oui' if course['conducteur_attribue'] else '❌ Non'}")

# 2. Attendre 61 secondes
print(f"\n2. ⏳ Attente de 61 secondes pour tester > délai gratuit...")
print("   (Le délai gratuit est de 60 secondes)")
print("   Après 61s, annulation = 1er avertissement")

for i in range(61, 0, -1):
    print(f"   ⏰ {i} secondes restantes...", end='\r')
    time.sleep(1)

print("\n   ✅ 61 secondes écoulées!")

# 3. Annuler la course
print(f"\n3. ❌ Annulation après 61 secondes...")
response = requests.post(
    f"{BASE_URL}/api/courses/{COURSE_CODE}/annuler",
    headers={"Authorization": TOKEN_CLIENT},
    json={"raison": "changement_d_avis_apres_delai"}
)

print(f"   Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"✅ ANNULEEATION RÉUSSIE!")
    
    # Sauvegarder pour analyse
    with open('resultat_annulation_61s.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 RÉSULTAT COMPLET:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Analyser les avertissements
    actions = result.get('actions_appliquees', [])
    for action in actions:
        if action.get('type') == 'avertissement':
            print(f"\n⚠️ SYSTEME 3 STRIKES ACTIVÉ!")
            print(f"   Avertissement n°{action.get('avertissement_numero', 1)}")
            print(f"   Message: {action.get('message', '')}")
            
            if action.get('avertissement_numero', 0) == 1:
                print(f"   → Prochaine annulation > 60s = suspension 24h")
            elif action.get('avertissement_numero', 0) == 2:
                print(f"   → Prochaine annulation > 60s = amende 500 KMF + suspension")
                
elif response.status_code == 404:
    print("❌ Course non trouvée")
    print("   Vérifiez le code de course")
    
elif response.status_code == 500:
    print("❌ Erreur serveur")
    print(f"   Détails: {response.text[:200]}")
    
else:
    print(f"⚠️ Autre erreur: {response.text[:200]}")

# 4. Recommandations pour tester toute la séquence
print("\n" + "="*60)
print("🎯 POUR TESTER TOUTE LA SÉQUENCE 3 STRIKES")
print("="*60)
print("\nExécutez ces étapes:")
print("1. python test_annulation_apres_60s.py  → 1er avertissement")
print("2. Attendez 1 minute, ré-exécutez       → 2ème avertissement + suspension 24h")
print("3. Attendez 1 minute, ré-exécutez       → 3ème avertissement + amende 500 KMF")

print("\n📊 Dashboard PDG pour voir les amendes:")
print(f"   http://localhost:5001/admin/dashboard?token=cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b")

print("\n" + "="*60)