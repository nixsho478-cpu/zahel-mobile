# creer_course_test.py
import requests
import json

print("=" * 50)
print("📝 CRÉATION D'UNE COURSE DE TEST")
print("=" * 50)

# Token client (celui que vous avez créé)
token_client = "+26934011111"

# Données de la course
course_data = {
    "depart_lat": -11.698,
    "depart_lng": 43.256,
    "arrivee_lat": -11.704,
    "arrivee_lng": 43.261,
    "prix": 2000  # 2000 KMF
}

try:
    print(f"🚖 Client: {token_client}")
    print(f"📍 Départ: {course_data['depart_lat']}, {course_data['depart_lng']}")
    print(f"🏁 Arrivée: {course_data['arrivee_lat']}, {course_data['arrivee_lng']}")
    print(f"💰 Prix: {course_data['prix']} KMF")
    
    print("\n📤 Création de la course...")
    
    response = requests.post(
        "http://localhost:5001/api/courses/demander",
        headers={"Authorization": token_client},
        json=course_data,
        timeout=10
    )
    
    print(f"\n📥 Réponse: Status {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        code_course = result['course']['code']
        print(f"\n✅ COURSE CRÉÉE !")
        print("-" * 40)
        print(f"Code: {code_course}")
        print(f"Statut: {result['course']['statut']}")
        print(f"Conducteur attribué: {result['course']['conducteur_attribue']}")
        print(f"Prix: {result['course']['prix_convenu']} KMF")
        print("-" * 40)
        
        # Sauvegarder le code
        with open('code_course_test.txt', 'w') as f:
            f.write(code_course)
        
        print(f"\n💾 Code sauvegardé dans 'code_course_test.txt'")
        print("\n🎯 Maintenant, rafraîchissez l'app Kivy pour voir la course !")
        
    else:
        print(f"\n❌ Erreur: {response.text}")
        
except Exception as e:
    print(f"\n💥 Erreur: {e}")

print("\n" + "=" * 50)
input("Appuyez sur ENTREE pour continuer...")