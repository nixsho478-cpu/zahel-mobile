# test_commencer.py
import requests
import json

print("=" * 50)
print("🚗 TEST : COMMENCER UNE COURSE")
print("=" * 50)

# Informations
code_course = "ZAHEL-XKX6475"  # La course qu'on a acceptée plus tôt
token_conducteur = "ZH-327KYM"  # Le même conducteur

print(f"📋 Course à commencer : {code_course}")
print(f"👤 Conducteur : {token_conducteur}")

try:
    # 1. D'abord, vérifier le statut actuel de la course
    print(f"\n1. Vérification du statut actuel...")
    
    # Pour vérifier, on pourrait appeler une route GET /courses/<code>
    # Mais pour l'instant, on suppose qu'elle est 'acceptee'
    
    # 2. Commencer la course
    print(f"2. Début de la course...")
    
    url = f"http://localhost:5001/api/courses/{code_course}/commencer"
    headers = {"Authorization": token_conducteur}
    
    response = requests.post(url, headers=headers, timeout=10)
    
    print(f"\n✅ RÉPONSE REÇUE")
    print(f"   Statut : {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n🎉 SUCCÈS ! Course commencée")
        print("-" * 40)
        print(f"Course    : {result['course']['code']}")
        print(f"Statut    : {result['course']['statut']}")
        print(f"Début     : {result['course']['debut']}")
        print(f"Prix      : {result['course']['prix']} KMF")
        print(f"Message   : {result['message']}")
        print("-" * 40)
        
        print("\n✅ La route `commencer_course` FONCTIONNE !")
        
    elif response.status_code == 400:
        print(f"\n⚠️  Erreur : {response.json().get('error', 'Course non acceptée')}")
        print("   La course n'est peut-être pas au statut 'acceptee'")
        
    elif response.status_code == 403:
        print(f"\n❌ Cette course ne vous est pas attribuée")
        
    elif response.status_code == 404:
        print(f"\n❌ Course non trouvée")
        
    else:
        print(f"\n⚠️  Autre erreur : {response.text}")
        
except Exception as e:
    print(f"\n💥 Erreur : {e}")

print("\n" + "=" * 50)
input("Appuie sur ENTREE pour continuer...")