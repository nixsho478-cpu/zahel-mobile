# creer_course_avec_conducteur.py
import requests
import json

print("🚗 CRÉATION COURSE AVEC CONDUCTEUR DISPONIBLE")
print("="*50)

token_client = "+26934011111"
url = "http://localhost:5001/api/courses/demander"

data = {
    "depart_lat": -11.698,
    "depart_lng": 43.256,
    "arrivee_lat": -11.704,
    "arrivee_lng": 43.261,
    "prix": 1500
}

print("📤 Création de la course...")
response = requests.post(url, headers={"Authorization": token_client}, json=data, timeout=10)

print(f"📥 Status: {response.status_code}")

if response.status_code == 201:
    result = response.json()
    course = result['course']
    
    print("✅ COURSE CRÉÉE AVEC SUCCÈS!")
    print(f"Code: {course['code']}")
    print(f"Statut: {course['statut']}")
    print(f"Conducteur attribué: {'✅ Oui' if course['conducteur_attribue'] else '❌ Non'}")
    print(f"Message: {course['message']}")
    
    # Sauvegarder pour les tests
    with open('course_test_active.txt', 'w') as f:
        f.write(course['code'])
    
    print(f"\n📁 Code sauvegardé: {course['code']}")
    
    if course['conducteur_attribue']:
        print("\n🎯 Prochaine étape:")
        print(f"   Conducteur ZH-327KYM peut accepter la course:")
        print(f"   POST /api/courses/{course['code']}/accepter")
    else:
        print("\n⚠️ Aucun conducteur n'a encore été attribué")
        
else:
    print(f"❌ Erreur: {response.text}")