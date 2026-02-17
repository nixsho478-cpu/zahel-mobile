# test_annulation_simple.py - VERSION FINALE
import requests
import json
import time

print("🧪 TEST ANNULATION CLIENT")
print("="*50)

# Token client
token_client = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"

# 1. Créer une nouvelle course
print("1. 📝 Création d'une course...")
course_data = {
    "depart_lat": -11.698,
    "depart_lng": 43.256,
    "arrivee_lat": -11.704,
    "arrivee_lng": 43.261,
    "prix": 1200
}

try:
    response = requests.post(
        "http://localhost:5001/api/courses/demander",
        headers={"Authorization": token_client},
        json=course_data,
        timeout=10
    )
    
    print(f"📥 Status création: {response.status_code}")
    
    # CORRECTION : La création réussit avec 201, pas 200
    if response.status_code in [200, 201]:  # <-- IMPORTANT
        result = response.json()
        course = result['course']
        course_code = course['code']
        print(f"✅ Course créée: {course_code}")
        print(f"   Statut: {course['statut']}")
        print(f"   Message: {course['message']}")
        
        # 2. Attendre 2 secondes (simuler > 60s)
        print("\n2. ⏳ Attente de 2 secondes (simule > 60s)...")
        time.sleep(2)
        
        # 3. Annuler la course
        print("\n3. 🚫 Annulation de la course...")
        annulation_data = {
            "raison": "changement_d_avis"
        }
        
        response_annulation = requests.post(
            f"http://localhost:5001/api/courses/{course_code}/annuler",
            headers={"Authorization": token_client},
            json=annulation_data,
            timeout=10
        )
        
        print(f"📥 Status annulation: {response_annulation.status_code}")
        
        if response_annulation.status_code == 200:
            result_annulation = response_annulation.json()
            print(f"\n✅ ANNULATION RÉUSSIE !")
            print(f"   Course: {result_annulation.get('course')}")
            print(f"   Statut: {result_annulation.get('statut')}")
            print(f"   Annulé par: {result_annulation.get('annule_par')}")
            
            actions = result_annulation.get('actions_appliquees', [])
            if actions:
                print(f"\n   📋 ACTIONS APPLIQUÉES:")
                for action in actions:
                    print(f"     • Type: {action.get('type')}")
                    print(f"       Message: {action.get('message', 'N/A')}")
            else:
                print(f"\n   ℹ️  Aucune action spécifique appliquée")
                
        else:
            print(f"\n❌ Erreur annulation: {response_annulation.text}")
            
    else:
        # CE N'EST PAS UNE ERREUR SI LE STATUS EST 201 !
        print(f"\n⚠️  Status inattendu: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"\n💥 Exception: {e}")

print("\n" + "="*50)
input("Appuyez sur Entrée pour continuer...")