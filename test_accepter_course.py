# test_accepter_course.py
import requests
import json

print("🚗 TEST ACCEPTATION COURSE PAR CONDUCTEUR")
print("="*50)

code_course = "ZAHEL-ASS8325"  # La course que vous venez de créer
token_conducteur = "ZH-327KYM"  # Conducteur de test

print(f"Course à accepter : {code_course}")
print(f"Conducteur : {token_conducteur}")

try:
    # 1. Accepter la course
    print(f"\n📤 Envoi de l'acceptation...")
    url = f"http://localhost:5001/api/courses/{code_course}/accepter"
    headers = {"Authorization": token_conducteur}
    
    response = requests.post(url, headers=headers, timeout=10)
    print(f"📥 Réponse reçue")
    print(f"   Status : {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCÈS COMPLET !")
        print(f"   Course : {result['course']['code']}")
        print(f"   Statut : {result['course']['statut']}")
        print(f"   Prix : {result['course']['prix']} KMF")
        print(f"   Message : {result['message']}")
        
    elif response.status_code == 404:
        print(f"\n❌ Course non trouvée : {code_course}")
    elif response.status_code == 403:
        print(f"\n❌ Cette course ne vous est pas attribuée")
    else:
        print(f"\n⚠️  Autre erreur : {response.text[:200]}")
        
except Exception as e:
    print(f"\n💥 Exception : {e}")

print("\n" + "="*50)
input("Appuyez sur Entrée pour continuer...")