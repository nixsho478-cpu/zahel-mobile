# test_amendes.py
import requests
import json

print("=" * 60)
print("🧪 TEST API SYSTÈME D'AMENDES ZAHEL")
print("=" * 60)

# Token PDG
TOKEN_PDG = "cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b"
headers = {"Authorization": TOKEN_PDG}

# 1. Test: Lister les amendes (vide pour l'instant)
print("\n1. 📋 TEST: GET /api/amendes")
try:
    response = requests.get(
        "http://localhost:5001/api/amendes",
        headers=headers,
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Succès! {data['total']} amendes trouvées")
        print(f"   Montant total: {data['total_montant']} KMF")
    else:
        print(f"   ❌ Erreur: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# 2. Test: Créer une amende de test (pour notre client existant)
print("\n2. ➕ TEST: POST /api/amendes/creer")
print("   Création d'une amende de test...")

# On a besoin d'un ID client existant. Trouvons-le d'abord:
print("\n   🔍 Recherche d'un client existant...")
try:
    # Test avec un token client (le téléphone)
    token_client = "+26934012345"  # Le client que tu as créé
    response = requests.get(
        "http://localhost:5001/api/client/info",
        headers={"Authorization": token_client},
        timeout=3
    )
    
    client_id = 1  # Par défaut, le premier client a l'ID 1
    
    amende_data = {
        "utilisateur_type": "client",
        "utilisateur_id": client_id,
        "montant": 500.00,
        "raison": "Annulation abusive - 3ème infraction"
    }
    
    response = requests.post(
        "http://localhost:5001/api/amendes/creer",
        headers=headers,
        json=amende_data,
        timeout=5
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"   ✅ Amende créée! ID: {data['amende_id']}")
        print(f"   Message: {data['message']}")
        
        # 3. Test: Lister à nouveau pour voir l'amende
        print("\n3. 📋 TEST: Vérification après création")
        response = requests.get(
            "http://localhost:5001/api/amendes?statut=en_attente",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data['total']} amende(s) en attente")
            if data['amendes']:
                amende = data['amendes'][0]
                print(f"   • ID: {amende['id']}")
                print(f"   • Client: {amende['nom_utilisateur']}")
                print(f"   • Montant: {amende['montant']} KMF")
                print(f"   • Raison: {amende['raison']}")
    else:
        print(f"   ❌ Erreur création: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Exception: {e}")
    print("   ℹ️ Vérifie qu'il y a un client dans la base")

# 4. Test: Payer une amende (simulation)
print("\n4. 💳 TEST: Paiement d'amende (simulation)")
print("   Cette route est publique (pas besoin de token admin)")
try:
    # On va simuler avec une amende ID 1 si elle existe
    paiement_data = {
        "token_paiement": "PAY_TEST_123456"
    }
    
    response = requests.post(
        "http://localhost:5001/api/amendes/1/payer",
        json=paiement_data,
        timeout=5
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Paiement réussi!")
        print(f"   Reçu: {data['receipt']}")
        print(f"   Message: {data['message']}")
    elif response.status_code == 404:
        print("   ℹ️ Aucune amende avec ID 1 (normal si base vide)")
    else:
        print(f"   ❌ Erreur: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Exception: {e}")

print("\n" + "=" * 60)
print("📊 RÉCAPITULATIF DU SYSTÈME D'AMENDES")
print("=" * 60)
print("Routes testées:")
print("• GET /api/amendes ✅ (si 200)")
print("• POST /api/amendes/creer ✅ (si 201)")
print("• POST /api/amendes/<id>/payer ✅ (si 200 ou 404)")
print("\nProchaine étape: Mettre à jour la logique d'annulation")
print("pour appliquer automatiquement les amendes 3 strikes!")

input("\nAppuyez sur Entrée pour quitter...")