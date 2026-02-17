# creer_amende_test_corrige.py
import requests
import json

print("=" * 60)
print("🎯 CRÉATION AMENDE - VERSION CORRIGÉE")
print("=" * 60)

TOKEN_PDG = "cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b"

# 1. D'abord, vérifier les clients existants
print("\n1. 🔍 Liste des clients existants...")
try:
    # On va chercher un client directement dans la base via API
    # Essayons plusieurs approches :
    
    # Option A: Tester la création avec un ID connu
    print("   Option A: Tester avec différents IDs...")
    
    for client_id in [1, 2, 3, 4]:
        print(f"   Test ID {client_id}...")
        try:
            # ESSAYONS SANS ACCENT D'ABORD
            response = requests.post(
                "http://localhost:5001/api/amendes/creer",  # SANS ACCENT
                headers={"Authorization": TOKEN_PDG},
                json={
                    "utilisateur_type": "client",
                    "utilisateur_id": client_id,
                    "montant": 500 + (client_id * 100),  # Différents montants
                    "raison": f"Test dashboard - Client ID {client_id}"
                },
                timeout=3
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"   ✅ SUCCÈS avec ID {client_id} !")
                print(f"      Amende ID: {result.get('amende_id')}")
                break
                
            elif response.status_code == 404:
                print(f"   ❌ Client ID {client_id} non trouvé")
                continue
                
            else:
                print(f"   ❌ Erreur {response.status_code}: {response.text[:100]}")
                # Essayons avec accent
                print("   Tentative avec accent...")
                response = requests.post(
                    "http://localhost:5001/api/amendes/créer",  # AVEC ACCENT
                    headers={"Authorization": TOKEN_PDG},
                    json={
                        "utilisateur_type": "client",
                        "utilisateur_id": client_id,
                        "montant": 500 + (client_id * 100),
                        "raison": f"Test dashboard - Client ID {client_id}"
                    },
                    timeout=3
                )
                
                if response.status_code == 201:
                    result = response.json()
                    print(f"   ✅ SUCCÈS (avec accent) ID {client_id} !")
                    break
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            continue
            
except Exception as e:
    print(f"❌ Erreur générale: {e}")

# 2. Si ça ne marche pas, créer d'abord un client test
print("\n2. 👥 Création d'un client test si nécessaire...")
try:
    # Essayer de créer un client d'abord
    print("   Tentative création client...")
    client_data = {
        "nom": "Client Amende Test",
        "telephone": "+26934033333",  # Nouveau numéro
        "password": "test123",
        "nationalite": "Comorienne"
    }
    
    response = requests.post(
        "http://localhost:5001/api/clients/inscription",
        json=client_data,
        timeout=5
    )
    
    if response.status_code in [200, 201]:
        client_result = response.json()
        new_client_id = client_result.get('client', {}).get('id')
        print(f"   ✅ Client créé ! ID: {new_client_id}")
        
        # Maintenant créer l'amende pour ce client
        print(f"   Création amende pour client ID {new_client_id}...")
        amende_response = requests.post(
            "http://localhost:5001/api/amendes/creer",  # Sans accent
            headers={"Authorization": TOKEN_PDG},
            json={
                "utilisateur_type": "client",
                "utilisateur_id": new_client_id,
                "montant": 850,
                "raison": "Test dashboard - Client nouvellement créé"
            },
            timeout=5
        )
        
        if amende_response.status_code == 201:
            amende_result = amende_response.json()
            print(f"   ✅ AMENDE CRÉÉE !")
            print(f"      ID: {amende_result.get('amende_id')}")
            print(f"      Client: Client Amende Test")
            print(f"      Montant: 850 KMF")
            
    else:
        print(f"   ❌ Erreur création client: {response.status_code}")
        print(f"      {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Exception: {e}")

# 3. Vérification finale
print("\n3. 📊 Vérification finale...")
try:
    response = requests.get(
        "http://localhost:5001/api/amendes",
        headers={"Authorization": TOKEN_PDG},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Total amendes: {data['total']}")
        print(f"   Montant total: {data['total_montant']} KMF")
        
        if data['amendes']:
            print("   Liste des amendes:")
            for amende in data['amendes']:
                print(f"   - #{amende['id']}: {amende['montant']} KMF - {amende['statut']}")
        else:
            print("   ❌ Aucune amende trouvée")
            
except Exception as e:
    print(f"   ❌ Erreur vérification: {e}")

print("\n" + "=" * 60)
print("📌 PROCHAINE ÉTAPE:")
print("1. Ouvrez votre dashboard")
print("2. Cliquez sur 'Amendes en attente'")
print("3. Si amendes existent → testez les boutons")
print("4. Sinon → vérifiez api_zahel.py ligne ~530-550")
print("=" * 60)

input("\nAppuyez sur Entrée pour voir les routes existantes...")

# 4. Vérifier toutes les routes
print("\n4. 🗺️ Routes API disponibles...")
try:
    # Test des endpoints clés
    endpoints = [
        ("/api/amendes", "GET"),
        ("/api/amendes/creer", "POST"),
        ("/api/amendes/créer", "POST"),
        ("/api/amendes/create", "POST"),
        ("/api/clients/inscription", "POST"),
        ("/api/admin/statistiques", "GET")
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                r = requests.get(f"http://localhost:5001{endpoint}", 
                                headers={"Authorization": TOKEN_PDG} if "admin" in endpoint else None,
                                timeout=2)
            else:
                r = requests.post(f"http://localhost:5001{endpoint}", 
                                 headers={"Authorization": TOKEN_PDG} if "amendes" in endpoint else None,
                                 json={"test": "data"} if method == "POST" else None,
                                 timeout=2)
            
            if r.status_code != 404:
                print(f"   ✅ {method} {endpoint}: {r.status_code}")
            else:
                print(f"   ❌ {method} {endpoint}: 404 (Non trouvé)")
                
        except Exception as e:
            print(f"   ❌ {method} {endpoint}: Erreur - {e}")
            
except Exception as e:
    print(f"   ❌ Exception routes: {e}")