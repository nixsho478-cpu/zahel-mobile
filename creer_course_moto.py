# creer_course_moto.py
import requests
import json

print("🏍️ CRÉATION D'UNE COURSE 'moto'")
print("=" * 50)

try:
    # Connexion client
    print("\n1. 🔐 CONNEXION CLIENT")
    response = requests.post(
        'http://localhost:5001/api/client/login',
        json={'telephone': '+26934011111', 'password': 'test123'},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    
    if not response.ok:
        print(f"❌ Échec: {response.text}")
        exit()
    
    client_data = response.json()
    token = client_data.get('token')
    print(f"✅ Token: {token}")
    
    # Créer course "moto"
    print("\n2. 📝 CRÉATION COURSE 'moto'")
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    
    course_data = {
        'depart_lat': -11.700,
        'depart_lng': 43.250,
        'arrivee_lat': -11.720,
        'arrivee_lng': 43.270,
        'prix': 1500.0,
        'categorie': 'moto'  # Catégorie moto
    }
    
    response2 = requests.post(
        'http://localhost:5001/api/courses/demander',
        headers=headers,
        json=course_data,
        timeout=10
    )
    
    print(f"Status: {response2.status_code}")
    
    if response2.ok:
        course_info = response2.json()
        print(f"\n✅ SUCCÈS !")
        print(f"   Code: {course_info.get('course', {}).get('code')}")
        print(f"   Catégorie: 'moto'")
        
        # Vérifier dans la base
        print(f"\n3. 📋 VÉRIFICATION BASE DE DONNÉES")
        print("-" * 30)
        
        import sqlite3
        conn = sqlite3.connect(r'C:\Users\USER\Desktop\zahel\backend\zahel_secure.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT code_unique, categorie_demande, statut, prix_convenu
            FROM courses 
            ORDER BY date_demande DESC 
            LIMIT 3
        ''')
        
        for row in cursor.fetchall():
            print(f"   • {row[0]} - {row[1]} - {row[2]} - {row[3]} KMF")
        
        conn.close()
        
    else:
        print(f"❌ Erreur: {response2.text}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()