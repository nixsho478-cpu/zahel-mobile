# get_token.py - Version avec timeout
import requests
import json
import time

print("=" * 50)
print("🔐 OBTENTION DU TOKEN PDG ZAHEL")
print("=" * 50)

url = "http://localhost:5001/api/admin/login"
data = {
    "username": "pdg_zahel",
    "password": "ZAHEL_PDG_2024_CHANGER"
}

try:
    print("📡 Connexion au serveur (timeout: 10s)...")
    
    # Ajout d'un timeout pour ne pas bloquer
    response = requests.post(url, json=data, timeout=10)
    
    print(f"✅ Réponse reçue - Statut : {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        token = result['token']
        
        print("\n🎉 TOKEN OBTENU AVEC SUCCÈS !")
        print("=" * 40)
        print(f"🔑 Token : {token[:50]}...")  # Affiche seulement les 50 premiers caractères
        print("=" * 40)
        
        # Sauvegarde
        with open("token_pdg.txt", "w") as f:
            f.write(token)
        print("\n💾 Token sauvegardé dans 'token_pdg.txt'")
        
        print("\n🌐 ACCÈS PANEL PDG :")
        print("=" * 40)
        print(f"http://localhost:5001/admin/secret?token={token}")
        print("=" * 40)
        
    else:
        print(f"\n❌ Erreur HTTP : {response.status_code}")
        print(f"Message : {response.text}")
        
except requests.exceptions.Timeout:
    print("\n⏰ TIMEOUT : Le serveur ne répond pas après 10 secondes")
    print("Vérifie que le serveur tourne bien !")
    
except requests.exceptions.ConnectionError:
    print("\n🔌 ERREUR DE CONNEXION : Impossible de joindre localhost:5001")
    print("1. Le serveur est-il démarré ?")
    print("2. Vérifie dans Chrome : http://localhost:5001")
    
except Exception as e:
    print(f"\n💥 Erreur inattendue : {type(e).__name__}")
    print(f"Détails : {e}")

print("\n" + "=" * 50)
input("Appuie sur ENTREE pour quitter...")