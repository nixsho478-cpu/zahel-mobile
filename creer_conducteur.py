# creer_conducteur.py
import requests
import json

print("=" * 50)
print("👤 CRÉATION CONDUCTEUR DE TEST POUR ZAHEL")
print("=" * 50)

# URL de l'API
url = "http://localhost:5001/api/conducteurs/inscription"

# Données du conducteur test
conducteur_test = {
    "nom": "Ahmed Test",
    "telephone": "+26934012345",
    "password": "zahel2024",
    "nationalite": "Comorienne",
    "numero_identite": "CI-TEST-001",
    "categorie": "classique",
    "marque": "Toyota",
    "modele": "Corolla 2020",
    "couleur": "Bleu",
    "plaque": "TEST-001-COM"
}

print(f"📡 Envoi à : {url}")
print(f"📋 Données : {json.dumps(conducteur_test, indent=2)}")

try:
    # Envoyer la requête
    response = requests.post(url, json=conducteur_test, timeout=10)
    
    print(f"\n✅ RÉPONSE REÇUE - Statut : {response.status_code}")
    
    if response.status_code == 201:
        resultat = response.json()
        print("\n🎉 CONDUCTEUR CRÉÉ AVEC SUCCÈS !")
        print("-" * 40)
        print(f"Immatricule : {resultat['conductor']['immatricule']}")
        print(f"Nom         : {resultat['conductor']['nom']}")
        print(f"Téléphone   : {conducteur_test['telephone']}")
        print(f"Véhicule    : {conducteur_test['marque']} {conducteur_test['modele']}")
        print(f"Categorie   : {conducteur_test['categorie']}")
        print("-" * 40)
        
        # Sauvegarder les infos pour les tests
        infos = {
            'immatricule': resultat['conductor']['immatricule'],
            'telephone': conducteur_test['telephone'],
            'password': conducteur_test['password']
        }
        
        with open('infos_conducteur_test.json', 'w') as f:
            json.dump(infos, f, indent=2)
        
        print("\n💾 Informations sauvegardées dans 'infos_conducteur_test.json'")
        
    else:
        print(f"\n❌ ERREUR : {response.status_code}")
        print(f"Détails : {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n🔌 ERREUR : Impossible de se connecter au serveur")
    print("Vérifie que le serveur tourne : python api_zahel.py")
    
except Exception as e:
    print(f"\n💥 ERREUR INATTENDUE : {type(e).__name__}")
    print(f"Détails : {e}")

print("\n" + "=" * 50)
input("Appuie sur ENTREE pour continuer...")