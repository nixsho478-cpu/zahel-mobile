# creer_course_non_attribuee.py
import requests
import json

print("=" * 50)
print("🚖 CRÉATION COURSE NON ATTRIBUÉE")
print("=" * 50)

# Méthode 1 : Via API (si vous modifiez le backend)
token_client = "+26934011111"

course_data = {
    "depart_lat": -11.700,
    "depart_lng": 43.250,
    "arrivee_lat": -11.710,
    "arrivee_lng": 43.265,
    "prix": 1500,
    "attribution_auto": False  # Nouveau paramètre si vous l'ajoutez à l'API
}

try:
    response = requests.post(
        "http://localhost:5001/api/courses/demander",
        headers={"Authorization": token_client},
        json=course_data,
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        course = data['course']
        print(f"\n✅ COURSE CRÉÉE:")
        print(f"   Code: {course['code']}")
        print(f"   Statut: {course['statut']}")
        print(f"   Attribuée: {course['conducteur_attribue']}")
        print(f"   Message: {course['message']}")
        
        if not course['conducteur_attribue']:
            print("\n🎯 PARFAIT ! La course n'est pas attribuée.")
            print("   Elle devrait apparaître dans l'app Kivy !")
        else:
            print("\n⚠️ La course a été attribuée automatiquement.")
            print("   Il faut modifier l'API pour désactiver l'attribution auto.")
            
    else:
        print(f"\n❌ Erreur: {data.get('error')}")
        
except Exception as e:
    print(f"\n💥 Erreur: {e}")

print("\n" + "=" * 50)

# Méthode 2 : Directement dans la base
print("\n📝 Option 2 : Insérer directement en base")
import sqlite3
conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Trouver un client
cursor.execute('SELECT id FROM clients LIMIT 1')
client = cursor.fetchone()

if client:
    import random
    import datetime
    
    code = f"ZAHEL-{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.randint(1000, 9999)}"
    
    cursor.execute('''
        INSERT INTO courses (
            code_unique, client_id, conducteur_id, statut,
            depart_lat, depart_lng, arrivee_lat, arrivee_lng,
            prix_convenu, created_at
        ) VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        code, client[0], 'en_attente',
        -11.702, 43.255, -11.708, 43.260,
        1800, datetime.datetime.now().isoformat()
    ))
    
    conn.commit()
    print(f"✅ Course {code} créée avec conducteur_id = NULL")
    print("   Elle devrait apparaître dans /api/courses/disponibles")
else:
    print("❌ Aucun client trouvé dans la base")

conn.close()

input("\nAppuyez sur ENTREE pour continuer...")