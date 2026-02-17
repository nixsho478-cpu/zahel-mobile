# test_simple_luxe.py
import requests
import json

API_BASE = "http://localhost:5001"

def test_simple():
    print("=== TEST SIMPLE (sans affichage JSON) ===")
    
    # 1. Connexion
    print("\n1. Connexion...")
    login_data = {'telephone': '+26934011111', 'password': 'test123'}
    login_resp = requests.post(f"{API_BASE}/api/client/login", json=login_data)
    
    print(f"Status: {login_resp.status_code}")
    print(f"Text: {login_resp.text[:100]}...")
    
    if login_resp.status_code != 200:
        print("❌ Connexion échouée")
        return
    
    token = login_resp.json().get('token')
    if not token:
        print("❌ Pas de token dans la réponse")
        return
    
    print(f"✅ Token obtenu ({len(token)} caractères)")
    
    # 2. Création course
    print("\n2. Création course LUXE...")
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    
    course_resp = requests.post(f"{API_BASE}/api/courses/demander", json={
        'depart_lat': -11.6980,
        'depart_lng': 43.2560,
        'arrivee_lat': -11.7100,
        'arrivee_lng': 43.2650,
        'prix': 2700,
        'categorie': 'luxe'
    }, headers=headers)
    
    print(f"Status: {course_resp.status_code}")
    print(f"Text: {course_resp.text[:200]}")
    
    if course_resp.status_code == 201:
        print("✅ Course créée avec succès !")
        
        # Essayer de parser JSON
        try:
            data = course_resp.json()
            print(f"\n✅ JSON parsé: {data}")
            
            if 'course' in data:
                course_code = data['course']['code']
                print(f"\n3. Vérification timer luxe pour {course_code}...")
                
                check_resp = requests.get(f"{API_BASE}/api/courses/{course_code}/check_luxe")
                print(f"Check status: {check_resp.status_code}")
                print(f"Check response: {check_resp.text}")
        except:
            print("⚠️  Réponse non-JSON, vérifiez les logs du serveur")
    
    # 3. Vérifier les logs du serveur
    print("\n=== CONSEILS ===")
    print("1. Vérifiez que le serveur API tourne")
    print("2. Regardez les logs du serveur pour l'erreur exacte")
    print("3. Assurez-vous qu'il n'y a plus de 'date_debut_recherche' dans le code")

if __name__ == "__main__":
    test_simple()