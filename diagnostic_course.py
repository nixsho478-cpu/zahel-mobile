# diagnostic_course.py - VERSION FINALEMENT CORRIGÉE
import requests
import json

print("🔍 DIAGNOSTIC CRÉATION COURSE - VERSION FINALE")
print("="*50)

# Utiliser le bon client
token_client = "+26934011111"  # Client Test existant
print(f"👤 Client: {token_client}")

url = "http://localhost:5001/api/courses/demander"

# ⚠️ CORRECTION ICI : utiliser 'lng' minuscule, pas 'Ing' avec majuscule I
data = {
    "depart_lat": -11.698,
    "depart_lng": 43.256,      # <-- CORRIGÉ : 'lng' pas 'Ing'
    "arrivee_lat": -11.704,
    "arrivee_lng": 43.261,     # <-- CORRIGÉ : 'lng' pas 'Ing'
    "prix": 1500
}

print(f"📍 Départ: {data['depart_lat']}, {data['depart_lng']}")
print(f"🎯 Arrivée: {data['arrivee_lat']}, {data['arrivee_lng']}")
print(f"💰 Prix: {data['prix']} KMF")

print("\n📤 Envoi de la requête...")
try:
    response = requests.post(url, headers={"Authorization": token_client}, json=data, timeout=10)
    
    print(f"📥 Réponse reçue")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCÈS TOTAL ! Course créée!")
        result = response.json()
        print(f"Code course: {result['course']['code']}")
        print(f"Statut: {result['course']['statut']}")
        print(f"Prix convenu: {result['course']['prix_convenu']} KMF")
        
        # Sauvegarder le code pour les tests suivants
        course_code = result['course']['code']
        with open('derniere_course.txt', 'w') as f:
            f.write(course_code)
        print(f"\n📁 Code sauvegardé dans 'derniere_course.txt': {course_code}")
        
    elif response.status_code == 400:
        print("❌ Erreur 400 - Données invalides")
        print(f"Détails: {response.text}")
        
    elif response.status_code == 401:
        print("❌ ERREUR 401 - Token invalide")
        print("Problème d'authentification")
        
    elif response.status_code == 500:
        print("❌ Erreur serveur 500")
        print(f"Détails: {response.text[:500]}")
        
    else:
        print(f"⚠️ Autre erreur ({response.status_code}): {response.text[:200]}")
        
except Exception as e:
    print(f"💥 Exception: {e}")
    print("Vérifiez que le serveur tourne: http://localhost:5001")