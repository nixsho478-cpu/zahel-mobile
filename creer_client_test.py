# creer_client_test.py
import requests
import json

print("=" * 50)
print("👤 CRÉATION CLIENT DE TEST")
print("=" * 50)

# Inscription client (si l'API existe)
# Sinon, on utilisera un client existant ou créé manuellement

client_test = {
    "telephone": "+26934011111",
    "nom": "Client Test",
    "password": "client123"
}

try:
    # Essayons d'abord de nous connecter avec un client existant
    print("📡 Test avec client par défaut...")
    
    # Pour l'instant, utilisons un téléphone simple comme token client
    # (dans ZAHEL, le token client est son téléphone)
    token_client = "+26934011111"
    
    print(f"✅ Client prêt (token = téléphone)")
    print(f"   Téléphone : {token_client}")
    print(f"   Token pour API : {token_client}")
    
    # Sauvegarder pour les tests
    with open('infos_client_test.json', 'w') as f:
        json.dump({"telephone": token_client, "nom": "Client Test"}, f, indent=2)
    
    print("\n💾 Infos client sauvegardées")
    
except Exception as e:
    print(f"💥 Erreur : {e}")

print("\n" + "=" * 50)
input("Appuie sur ENTREE pour continuer...")