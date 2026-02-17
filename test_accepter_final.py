# test_accepter_final.py
import requests
import json

print("=" * 50)
print("✅ TEST FINAL : ACCEPTER UNE COURSE")
print("=" * 50)

# Informations
code_course = "ZAHEL-XKX6475"
token_conducteur = "ZH-327KYM"  # L'immatricule = token

print(f"📋 Course à accepter : {code_course}")
print(f"👤 Conducteur : {token_conducteur}")

try:
    # 1. Accepter la course
    print(f"\n📡 Envoi de l'acceptation...")
    
    url = f"http://localhost:5001/api/courses/{code_course}/accepter"
    headers = {"Authorization": token_conducteur}
    
    response = requests.post(url, headers=headers, timeout=10)
    
    print(f"\n✅ RÉPONSE REÇUE")
    print(f"   Statut : {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n🎉🎉🎉 SUCCÈS COMPLET ! 🎉🎉🎉")
        print("-" * 50)
        print(f"Course : {result['course']['code']}")
        print(f"Statut : {result['course']['statut']}")
        print(f"Prix : {result['course']['prix']} KMF")
        print(f"Acceptation : {result['course']['acceptation']}")
        print(f"Message : {result['message']}")
        print("-" * 50)
        
        print("\n✅ La route `accepter_course` FONCTIONNE PARFAITEMENT !")
        
    elif response.status_code == 404:
        print(f"\n❌ Course non trouvée : {code_course}")
        print("   Vérifie le code de course")
        
    elif response.status_code == 403:
        print(f"\n❌ Cette course ne vous est pas attribuée")
        print("   Le conducteur n'est pas celui assigné à la course")
        
    else:
        print(f"\n⚠️  Autre erreur : {response.text}")
        
except Exception as e:
    print(f"\n💥 Erreur : {e}")

print("\n" + "=" * 50)
input("Appuie sur ENTREE pour continuer...")