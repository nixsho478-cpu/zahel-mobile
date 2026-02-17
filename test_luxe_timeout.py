# test_luxe_timeout.py
import requests
import json
import time

print("🧪 TEST SYSTÈME TIMEOUT LUXE")
print("=" * 60)

def test_complet():
    try:
        # 1. Connexion client
        print("\n1. 🔐 CONNEXION CLIENT")
        response = requests.post(
            'http://localhost:5001/api/client/login',
            json={'telephone': '+26934011111', 'password': 'test123'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if not response.ok:
            print(f"❌ Échec: {response.text}")
            return
        
        token = response.json().get('token')
        print(f"✅ Token: {token}")
        
        # 2. Créer une course LUXE
        print("\n2. 💎 CRÉATION COURSE LUXE")
        headers = {'Authorization': token}
        
        course_data = {
            'depart_lat': -11.698,
            'depart_lng': 43.256,
            'arrivee_lat': -11.720,
            'arrivee_lng': 43.270,
            'prix': 5000.0,  # Prix luxe
            'categorie': 'luxe'  # IMPORTANT : luxe
        }
        
        response2 = requests.post(
            'http://localhost:5001/api/courses/demander',
            headers=headers,
            json=course_data,
            timeout=10
        )
        
        print(f"Status: {response2.status_code}")
        
        if not response2.ok:
            print(f"❌ Échec création: {response2.text}")
            return
        
        course_info = response2.json()
        course_code = course_info.get('course', {}).get('code')
        print(f"✅ Course créée: {course_code}")
        print(f"✅ Catégorie: luxe")
        print(f"✅ Statut: {course_info.get('course', {}).get('statut')}")
        
        # 3. Vérifier immédiatement le statut luxe
        print("\n3. ⏱️  VÉRIFICATION IMMÉDIATE")
        time.sleep(2)
        
        response3 = requests.get(
            f'http://localhost:5001/api/courses/{course_code}/check_luxe',
            timeout=10
        )
        
        if response3.ok:
            check_data = response3.json()
            print(f"✅ API check: {check_data.get('success')}")
            print(f"✅ Is luxe: {check_data.get('is_luxe')}")
            print(f"✅ Timeout: {check_data.get('timeout')}")
            print(f"✅ Message: {check_data.get('message')}")
            
            if check_data.get('temps_ecoule'):
                print(f"✅ Temps écoulé: {check_data.get('temps_ecoule')}s")
                print(f"✅ Temps max: {check_data.get('temps_max')}s")
                print(f"✅ Temps restant: {check_data.get('temps_restant')}s")
        
        # 4. Simuler attente (pour test, on peut réduire le timeout dans la config)
        print("\n4. 🕐 SIMULATION ATTENTE (attendre 10s pour test)")
        print("   (Dans la vraie vie: 300s = 5 minutes)")
        
        for i in range(1, 4):
            time.sleep(3)
            print(f"   ... {i*3} secondes écoulées")
            
            response4 = requests.get(
                f'http://localhost:5001/api/courses/{course_code}/check_luxe',
                timeout=10
            )
            
            if response4.ok:
                data = response4.json()
                if data.get('timeout'):
                    print(f"   ⚠️  TIMEOUT DÉTECTÉ !")
                    break
        
        # 5. Option : changer en confort
        print("\n5. 🔄 TEST CHANGEMENT CONFORT (optionnel)")
        changer = input("Voulez-vous tester le changement luxe→confort ? (o/n): ")
        
        if changer.lower() == 'o':
            response5 = requests.post(
                f'http://localhost:5001/api/courses/{course_code}/switch_to_confort',
                timeout=10
            )
            
            print(f"Status: {response5.status_code}")
            if response5.ok:
                switch_data = response5.json()
                print(f"✅ Switch réussi!")
                print(f"✅ Message: {switch_data.get('message')}")
                if switch_data.get('course'):
                    print(f"✅ Nouveau prix: {switch_data['course'].get('nouveau_prix')} KMF")
            else:
                print(f"❌ Échec switch: {response5.text}")
        
        print("\n✅ TEST TERMINÉ !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complet()