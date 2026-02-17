# test_connexion.py
import requests
import json

print("=" * 50)
print("🔐 CONNEXION CONDUCTEUR ZAHEL")
print("=" * 50)

# Données de connexion du PREMIER conducteur qu'on a créé
donnees_connexion = {
    "telephone": "+26934012345",  # Ahmed Test
    "password": "zahel2024"
}

print(f"📞 Téléphone : {donnees_connexion['telephone']}")
print(f"🔑 Mot de passe : {donnees_connexion['password']}")

try:
    print("\n📡 Connexion en cours...")
    reponse = requests.post(
        "http://localhost:5001/api/conducteurs/connexion",
        json=donnees_connexion,
        timeout=5
    )
    
    print(f"\n✅ RÉPONSE REÇUE")
    print(f"   Statut : {reponse.status_code}")
    
    if reponse.status_code == 200:
        resultat = reponse.json()
        
        print("\n🎉 CONNEXION RÉUSSIE !")
        print("-" * 40)
        print(f"TOKEN : {resultat['token']}")
        print(f"Nom   : {resultat['conducteur']['nom']}")
        print(f"ID    : {resultat['conducteur']['id']}")
        print("-" * 40)
        
        # Sauvegarder le token pour les tests
        with open('token_conducteur_test.txt', 'w') as f:
            f.write(resultat['token'])
        
        print("\n💾 Token sauvegardé dans 'token_conducteur_test.txt'")
        print("📌 Ce token (immatricule) sert à s'authentifier pour les courses!")
        
    else:
        print(f"\n❌ ERREUR DE CONNEXION")
        print(f"   Détails : {reponse.text}")
        
except Exception as e:
    print(f"\n💥 ERREUR : {e}")

print("\n" + "=" * 50)
input("Appuie sur ENTREE pour continuer...")