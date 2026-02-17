# creer_amende_test.py
import requests
import json

print("=" * 60)
print("🎯 CRÉATION D'UNE AMENDE DE TEST POUR LE DASHBOARD")
print("=" * 60)

TOKEN_PDG = "cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b"

# 1. Trouver un client existant
print("\n1. 🔍 Recherche d'un client...")
try:
    # D'abord tester si l'API statistiques donne les infos clients
    response = requests.get(
        "http://localhost:5001/api/admin/statistiques",
        headers={"Authorization": TOKEN_PDG},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Statistiques OK: {data['statistiques']['clients']['total']} clients")
    else:
        print(f"❌ Erreur statistiques: {response.status_code}")
        print(f"Message: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

# 2. Créer une amende de test
print("\n2. 💰 Création de l'amende de test...")
amende_data = {
    "utilisateur_type": "client",
    "utilisateur_id": 1,  # ID du client test
    "montant": 750,  # 750 KMF
    "raison": "Test dashboard - Annulation abusive après 60 secondes"
}

try:
    response = requests.post(
        "http://localhost:5001/api/amendes/créer",
        headers={"Authorization": TOKEN_PDG},
        json=amende_data,
        timeout=5
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ AMENDE CRÉÉE AVEC SUCCÈS !")
        print(f"   ID: {result['amende_id']}")
        print(f"   Montant: 750 KMF")
        print(f"   Raison: {amende_data['raison']}")
        
        print(f"\n📋 POUR TESTER LE DASHBOARD:")
        print(f"1. Rafraîchissez le dashboard (F5)")
        print(f"2. Cliquez sur 'Amendes en attente'")
        print(f"3. Vous devriez voir 1 amende de 750 KMF")
        print(f"4. Testez les boutons 'Payer avec détails' et 'Détails complets'")
        
    elif response.status_code == 404:
        print("❌ Client non trouvé avec ID=1")
        print("Essayons avec ID=2...")
        
        # Essayer avec ID=2
        amende_data["utilisateur_id"] = 2
        response2 = requests.post(
            "http://localhost:5001/api/amendes/créer",
            headers={"Authorization": TOKEN_PDG},
            json=amende_data,
            timeout=5
        )
        
        if response2.status_code == 201:
            result = response2.json()
            print(f"✅ AMENDE CRÉÉE avec client ID=2 !")
            print(f"   ID: {result['amende_id']}")
        else:
            print(f"❌ Échec avec ID=2: {response2.status_code}")
            print(f"Message: {response2.text[:200]}")
            
    else:
        print(f"❌ Erreur création amende: {response.status_code}")
        print(f"Message: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

# 3. Vérifier les amendes existantes
print("\n3. 🔍 Vérification des amendes actuelles...")
try:
    response = requests.get(
        "http://localhost:5001/api/amendes",
        headers={"Authorization": TOKEN_PDG},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Amendes trouvées: {data['total']}")
        print(f"💰 Montant total: {data['total_montant']} KMF")
        
        if data['amendes']:
            for amende in data['amendes']:
                print(f"   - #{amende['id']}: {amende['montant']} KMF - {amende['statut']}")
        else:
            print("   Aucune amende trouvée")
            
except Exception as e:
    print(f"❌ Exception vérification: {e}")

print("\n" + "=" * 60)
print("📌 INSTRUCTIONS:")
print("1. Rafraîchissez votre dashboard (F5)")
print("2. Cliquez sur 'Amendes en attente'")
print("3. Testez les nouveaux boutons")
print("=" * 60)

input("\nAppuyez sur Entrée pour quitter...")