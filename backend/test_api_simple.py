# test_api_simple.py
import requests
import json

print("=" * 50)
print("TEST API RECHERCHE CONDUCTEUR")
print("=" * 50)

token = "cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b"
url = "http://localhost:5001/api/admin/conducteur/ZH-327KYM"

print(f"URL: {url}")
print(f"Token: {token[:20]}...")

try:
    response = requests.get(url, headers={"Authorization": token}, timeout=5)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCÈS ! API fonctionne !")
        print("-" * 40)
        print(f"Nom: {data['conducteur']['nom']}")
        print(f"Téléphone: {data['conducteur']['telephone']}")
        print(f"Courses: {data['conducteur']['performance']['courses_effectuees']}")
        print(f"Gains: {data['conducteur']['performance']['gains_totaux']} KMF")
        print(f"Véhicule: {data['conducteur']['vehicule']['marque']} {data['conducteur']['vehicule']['modele']}")
        print("-" * 40)
        print("\n🎉 La recherche conducteur fonctionne parfaitement !")
        print("Maintenant il faut mettre à jour le JavaScript du dashboard.")
    else:
        print(f"❌ Erreur: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
    print("Vérifie que le serveur tourne !")

print("\n" + "=" * 50)
input("Appuie sur Entrée pour quitter...")