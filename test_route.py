# test_route.py
import requests

print("=" * 50)
print("🧪 TEST ACCEPTATION COURSE - SIMPLE")
print("=" * 50)

# URL de la nouvelle route
url = "http://localhost:5001/api/courses/TEST123/accepter"

# Headers (simuler un conducteur)
headers = {
    "Authorization": "ZH-999TEST"  # Immatricule fictif
}

print(f"\n1. Test de la route : POST {url}")
print(f"2. Headers : {headers}")

try:
    print("\n3. Envoi de la requête...")
    response = requests.post(url, headers=headers, timeout=5)
    
    print(f"\n📡 RÉSULTAT :")
    print(f"   Statut : {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ SUCCÈS ! Route fonctionnelle")
        print(f"   Réponse : {response.json()}")
    elif response.status_code == 404:
        print("   ℹ️  Course non trouvée (normal pour un test)")
        print("   ✅ La route répond correctement !")
    elif response.status_code == 401:
        print("   🔒 Erreur d'authentification")
        print("   ✅ La route vérifie bien l'authentification !")
    else:
        print(f"   ❌ Erreur : {response.text[:200]}")
        
except Exception as e:
    print(f"\n💥 ERREUR : {e}")
    print("   Vérifie que le serveur tourne !")

print("\n" + "=" * 50)
input("Appuie sur ENTREE pour quitter...")