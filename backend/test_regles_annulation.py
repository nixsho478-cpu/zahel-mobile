# test_regles_annulation.py
import requests
import json
import time

print("🧪 TEST DES RÈGLES 3 STRIKES ZAHEL")
print("="*60)

# Tokens
TOKEN_PDG = "cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b"
TOKEN_CLIENT = "+26934012345"  # Ton client test
TOKEN_CONDUCTEUR = "ZH-327KYM"  # Ton conducteur test

def test_annulation_gratuite():
    """Test 1: Annulation dans les 60 secondes (gratuite)"""
    print("\n1. 🔄 TEST: Annulation dans les 60s (GRATUITE)")
    
    # D'abord créer une course
    course_data = {
        "depart_lat": -11.698,
        "depart_lng": 43.256,
        "arrivee_lat": -11.704,
        "arrivee_lng": 43.261,
        "prix": 1000
    }
    
    response = requests.post(
        "http://localhost:5001/api/courses/demander",
        headers={"Authorization": TOKEN_CLIENT},
        json=course_data,
        timeout=5
    )
    
    if response.status_code != 200:
        print("   ❌ Impossible de créer la course")
        return None
    
    course_code = response.json()['course']['code']
    print(f"   Course créée: {course_code}")
    
    # Annuler immédiatement (< 60s)
    time.sleep(1)  # Attendre 1 seconde seulement
    
    response = requests.post(
        f"http://localhost:5001/api/courses/{course_code}/annuler",
        headers={"Authorization": TOKEN_CLIENT},
        json={"raison": "changement_d_avis"},
        timeout=5
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Annulation réussie!")
        print(f"   Actions: {data.get('actions_appliquees', [])}")
        return data
    else:
        print(f"   ❌ Erreur: {response.text[:200]}")
        return None

def test_premier_avertissement():
    """Test 2: Première annulation après 60s (avertissement)"""
    print("\n2. ⚠️ TEST: 1ère annulation > 60s (AVERTISSEMENT)")
    
    # Pour simuler > 60s, on va tricher en modifiant la date dans la base
    # Ou on test avec une course créée il y a longtemps
    
    print("   (Ce test nécessite une course créée il y a > 60s)")
    print("   ℹ️ À tester manuellement avec Postman")
    return None

def test_client_absent():
    """Test 3: Conducteur annule pour client absent > 10min"""
    print("\n3. ⏰ TEST: Client absent > 10min (COMPENSATION)")
    
    # Créer une course
    course_data = {
        "depart_lat": -11.698,
        "depart_lng": 43.256,
        "arrivee_lat": -11.704,
        "arrivee_lng": 43.261,
        "prix": 2000
    }
    
    response = requests.post(
        "http://localhost:5001/api/courses/demander",
        headers={"Authorization": TOKEN_CLIENT},
        json=course_data,
        timeout=5
    )
    
    if response.status_code != 200:
        print("   ❌ Impossible de créer la course")
        return None
    
    course_code = response.json()['course']['code']
    print(f"   Course créée: {course_code}")
    
    # Simuler que le conducteur attend > 10min
    # Le conducteur annule pour "client_absent"
    response = requests.post(
        f"http://localhost:5001/api/courses/{course_code}/annuler",
        headers={"Authorization": TOKEN_CONDUCTEUR},
        json={
            "raison": "client_absent",
            "temps_attente": 15  # 15 minutes
        },
        timeout=5
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Annulation conducteur réussie!")
        
        # Vérifier la compensation
        for action in data.get('actions_appliquees', []):
            if action.get('type') == 'client_absent':
                print(f"   🎁 Compensation: {action.get('compensation_conducteur')}")
                print(f"   💰 Amende client: {action.get('amende_client')} KMF")
                print(f"   📝 Message: {action.get('message')}")
        
        return data
    else:
        print(f"   ❌ Erreur: {response.text[:200]}")
        return None

def verifier_etat_client():
    """Vérifier l'état du client après les tests"""
    print("\n4. 🔍 VÉRIFICATION ÉTAT CLIENT")
    
    # Utiliser la route recherche conducteur comme modèle
    # On n'a pas de route /api/client/info, donc on vérifie dans la base
    print("   Vérification via base de données...")
    
    # Vérifier les amendes en attente
    response = requests.get(
        "http://localhost:5001/api/amendes?statut=en_attente",
        headers={"Authorization": TOKEN_PDG},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   📋 Amendes en attente: {data['total']}")
        print(f"   💰 Montant total: {data['total_montant']} KMF")
        
        if data['amendes']:
            for amende in data['amendes']:
                print(f"   • ID {amende['id']}: {amende['montant']} KMF - {amende['raison']}")
    
    return True

# Exécution des tests
if __name__ == "__main__":
    print("\n🚀 LANCEMENT DES TESTS DE RÈGLES ZAHEL")
    print("="*60)
    
    # Test 1: Annulation gratuite
    # result1 = test_annulation_gratuite()
    
    # Test 2: Premier avertissement (à faire manuellement)
    # test_premier_avertissement()
    
    # Test 3: Client absent
    print("\n⚠️ ATTENTION: Ce test va créer une amende de 1000 KMF")
    print("pour le client (50% de 2000 KMF)")
    input("Appuyez sur Entrée pour continuer...")
    
    result3 = test_client_absent()
    
    # Vérification finale
    verifier_etat_client()
    
    print("\n" + "="*60)
    print("📊 RÉCAPITULATIF DES TESTS")
    print("="*60)
    print("Tests réalisés:")
    print("• Annulation gratuite (< 60s) - À tester avec Postman")
    print("• 1er avertissement (> 60s) - À tester avec Postman")
    print("• Client absent > 10min - Testé ✅")
    print("\n🎯 Prochaine étape: Ajouter l'interface amendes au dashboard PDG")
    
    input("\nAppuyez sur Entrée pour quitter...")