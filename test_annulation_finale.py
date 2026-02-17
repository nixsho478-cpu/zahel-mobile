# test_annulation_finale.py
import requests
import json
import time

print("🧪 TEST FINAL D'ANNULATION ET SYSTÈME D'AMENDES")
print("="*60)

# Configuration
TOKEN_CLIENT = "+26934011111"
TOKEN_CONDUCTEUR = "ZH-327KYM"
BASE_URL = "http://localhost:5001"

# 1. Créer une course pour le test
print("\n1. 📝 CRÉATION COURSE DE TEST")
print("-"*40)

course_data = {
    "depart_lat": -11.698,
    "depart_lng": 43.256,
    "arrivee_lat": -11.704,
    "arrivee_lng": 43.261,
    "prix": 1200
}

response = requests.post(
    f"{BASE_URL}/api/courses/demander",
    headers={"Authorization": TOKEN_CLIENT},
    json=course_data,
    timeout=10
)

if response.status_code != 201:
    print(f"❌ Erreur création: {response.status_code}")
    print(response.text)
    exit()

course_info = response.json()['course']
COURSE_CODE = course_info['code']
print(f"✅ Course créée: {COURSE_CODE}")
print(f"   Statut: {course_info['statut']}")
print(f"   Conducteur attribué: {'✅ Oui' if course_info['conducteur_attribue'] else '❌ Non'}")

# 2. Accepter la course par le conducteur (optionnel)
print("\n2. 🚗 CONDUCTEUR ACCEPTE LA COURSE")
print("-"*40)

response = requests.post(
    f"{BASE_URL}/api/courses/{COURSE_CODE}/accepter",
    headers={"Authorization": TOKEN_CONDUCTEUR},
    timeout=10
)

if response.status_code == 200:
    print("✅ Course acceptée par le conducteur")
    course_status = "acceptee"
else:
    print(f"⚠️ Le conducteur n'a pas accepté (ou déjà accepté): {response.status_code}")
    course_status = "en_attente"

# 3. Annuler la course (TEST CRITIQUE)
print("\n3. ❌ TEST ANNULEEATION CLIENT")
print("-"*40)
print("   Objectif: Vérifier les règles 3 strikes")
print("   Cette annulation est immédiate (< 60s)")
print("   Elle devrait être GRATUITE sans avertissement")

response = requests.post(
    f"{BASE_URL}/api/courses/{COURSE_CODE}/annuler",
    headers={"Authorization": TOKEN_CLIENT},
    json={"raison": "test_annulation_immediate"},
    timeout=10
)

print(f"📥 Status de l'annulation: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print("✅ ANNULEEATION RÉUSSIE !")
    print(f"   Statut course: {result.get('statut')}")
    print(f"   Annulé par: {result.get('annule_par')}")
    
    # Analyser les actions appliquées
    actions = result.get('actions_appliquees', [])
    if actions:
        print(f"\n📋 ACTIONS APPLIQUÉES:")
        for action in actions:
            action_type = action.get('type', 'inconnu')
            
            if action_type == 'annulation_gratuite':
                print(f"   🆓 ANNULEEATION GRATUITE")
                print(f"      Délai: {action.get('delai_secondes', 0):.0f} secondes")
                print(f"      Message: {action.get('message', '')}")
                
            elif action_type == 'avertissement':
                print(f"   ⚠️ AVERTISSEMENT #{action.get('avertissement_numero', 1)}")
                print(f"      Message: {action.get('message', '')}")
                if action.get('avertissement_numero', 0) == 1:
                    print(f"      Conséquence: Il reste 2 marge(s) d'erreur")
                    
            elif action_type == 'suspension_24h':
                print(f"   🚫 SUSPENSION 24 HEURES")
                print(f"      Jusqu'à: {action.get('suspension_jusque', 'N/A')}")
                print(f"      Message: {action.get('message', '')}")
                
            elif action_type == 'amende_suspension':
                print(f"   💰 AMENDE + SUSPENSION PERMANENTE")
                print(f"      Montant: {action.get('amende', 0)} KMF")
                print(f"      Message: {action.get('message', '')}")
                
            elif action_type == 'client_absent':
                print(f"   🚶 CLIENT ABSENT > 10min")
                print(f"      Compensation conducteur: {action.get('compensation_conducteur')}")
                print(f"      Amende client: {action.get('amende_client')} KMF")
                print(f"      Message: {action.get('message', '')}")
                
            else:
                print(f"   📝 {action_type.upper()}")
                print(f"      Détails: {action}")
    
    else:
        print("   ℹ️ Aucune action spécifique appliquée")
        
    # Vérifier si une amende a été appliquée
    if 'amende' in result and result['amende'] > 0:
        print(f"\n💰 AMENDE APPLIQUÉE: {result['amende']} KMF")
        print(f"   Message: {result.get('message_amende', '')}")
    else:
        print(f"\n✅ Aucune amende appliquée (annulation dans les délais)")
        
elif response.status_code == 400:
    print("❌ Erreur 400 - Requête invalide")
    print(f"   Détails: {response.text[:200]}")
    
elif response.status_code == 401:
    print("❌ Erreur 401 - Token invalide")
    
elif response.status_code == 500:
    print("❌ Erreur 500 - Problème serveur")
    print("   Regardez le terminal du serveur Flask pour l'erreur détaillée")
    
else:
    print(f"⚠️ Autre erreur: {response.status_code}")
    print(f"   Message: {response.text[:200]}")

# 4. Vérifier l'état du client après annulation
print("\n4. 👤 ÉTAT DU CLIENT APRÈS ANNULATION")
print("-"*40)
print("   (Pour vérifier s'il a reçu un avertissement)")

# Pour vérifier, on pourrait créer une autre course et voir si elle est bloquée
print("   Création d'une seconde course pour vérification...")

response2 = requests.post(
    f"{BASE_URL}/api/courses/demander",
    headers={"Authorization": TOKEN_CLIENT},
    json={
        "depart_lat": -11.698,
        "depart_lng": 43.256,
        "arrivee_lat": -11.704,
        "arrivee_lng": 43.261,
        "prix": 800
    },
    timeout=10
)

if response2.status_code == 201:
    print("   ✅ Client peut toujours créer des courses")
    print("   → Aucune sanction immédiate (normal pour 1ère annulation)")
    
    # Annuler cette course aussi pour tester 2ème avertissement
    course2_code = response2.json()['course']['code']
    requests.post(
        f"{BASE_URL}/api/courses/{course2_code}/annuler",
        headers={"Authorization": TOKEN_CLIENT},
        json={"raison": "test_2eme_annulation"}
    )
    
elif response2.status_code == 403:
    print("   ❌ Client SUSPENDU ou AMENDE IMPAYÉE")
    result = response2.json()
    if 'suspension_jusque' in result:
        print(f"   → Suspension jusqu'à: {result['suspension_jusque']}")
    if 'amende_en_cours' in result:
        print(f"   → Amende en cours: {result['amende_en_cours']} KMF")
else:
    print(f"   ⚠️ Autre statut: {response2.status_code}")

# 5. Recommandations pour tester les 3 strikes
print("\n" + "="*60)
print("🎯 POUR TESTER COMPLÈTEMENT LE SYSTÈME 3 STRIKES")
print("="*60)
print("\nMéthode 1: Avec Postman (recommandé)")
print("   1. Créer une course")
print("   2. Attendre > 60 secondes")
print("   3. Annuler → Doit donner 1er avertissement")
print("   4. Répéter 2 fois → 2ème: suspension 24h, 3ème: amende 500 KMF")
print("\nMéthode 2: Simuler > 60s dans la base")
print("   Modifier la date de création de la course dans la table 'courses'")
print("   Mettre une date vieille de > 60 secondes")

print("\n📊 Dashboard PDG pour suivre les amendes:")
print(f"   http://localhost:5001/admin/dashboard?token=cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b")

print("\n" + "="*60)
input("Appuyez sur Entrée pour terminer...")