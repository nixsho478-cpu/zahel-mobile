# test_final_luxe.py
import requests
import json

API_BASE = "http://localhost:5001"

def test_complet():
    print("=== TEST COMPLET COURSE LUXE ===")
    
    # 1. Connexion
    print("\n1. Connexion client...")
    login_response = requests.post(f"{API_BASE}/api/client/login", json={
        'telephone': '+26934011111',
        'password': 'test123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ Connexion échouée: {login_response.text}")
        return
    
    token = login_response.json()['token']
    print(f"✅ Token: {token[:20]}...")
    
    # 2. Créer course LUXE
    print("\n2. Création course LUXE...")
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    
    response = requests.post(f"{API_BASE}/api/courses/demander", json={
        'depart_lat': -11.6980,
        'depart_lng': 43.2560,
        'arrivee_lat': -11.7100,
        'arrivee_lng': 43.2650,
        'prix': 2700,
        'categorie': 'luxe',  # ⭐ TRÈS IMPORTANT
        'service': 'luxe'
    }, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        course_data = response.json()['course']
        course_code = course_data['code']
        
        # 3. Vérifier avec check_luxe
        print(f"\n3. Vérification timer luxe pour {course_code}...")
        check_response = requests.get(f"{API_BASE}/api/courses/{course_code}/check_luxe")
        
        print(f"Check status: {check_response.status_code}")
        print(f"Check result: {json.dumps(check_response.json(), indent=2)}")
        
        # 4. Vérifier dans la base
        print(f"\n4. Vérification directe base de données...")
        import sqlite3
        conn = sqlite3.connect(r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT code_unique, categorie_demande, date_debut_recherche_luxe 
            FROM courses WHERE code_unique = ?
        ''', (course_code,))
        
        row = cursor.fetchone()
        if row:
            print(f"✅ Trouvé dans DB:")
            print(f"   Code: {row['code_unique']}")
            print(f"   Catégorie: {row['categorie_demande']}")
            print(f"   Date début recherche luxe: {row['date_debut_recherche_luxe']}")
            
            # Vérification critique
            if row['categorie_demande'] == 'luxe':
                print("🎯 SUCCÈS : La course est bien catégorisée LUXE !")
            else:
                print(f"❌ ÉCHEC : Catégorie = {row['categorie_demande']} (devrait être 'luxe')")
                
            if row['date_debut_recherche_luxe']:
                print("🎯 SUCCÈS : date_debut_recherche_luxe est défini !")
            else:
                print("❌ ÉCHEC : date_debut_recherche_luxe est NULL")
        else:
            print("❌ Course non trouvée dans DB")
        
        conn.close()

if __name__ == "__main__":
    test_complet()