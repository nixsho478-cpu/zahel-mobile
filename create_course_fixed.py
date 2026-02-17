# create_course_fixed.py
import sqlite3
import datetime
import random
import string

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Générer un code unique
code = 'ZAHEL-TEST-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print(f"🎯 Création course test: {code}")

try:
    cursor.execute('''
        INSERT INTO courses (
            code_unique, client_id, conducteur_id,
            point_depart_lat, point_depart_lng, 
            point_arrivee_lat, point_arrivee_lng,
            prix_convenu, statut, date_demande
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        code, 3, None,  # client_id=3, conducteur_id=NULL
        -11.698, 43.256,  # Centre Ville Moroni
        -11.655, 43.265,  # Hôtel Itsandra
        180, 'en_attente', now  # Prix: 180 KMF
    ))
    
    conn.commit()
    print(f"✅ COURSE TEST CRÉÉE:")
    print(f"   Code: {code}")
    print(f"   Client: 3 (+26934011111)")
    print(f"   Conducteur: AUCUN")
    print(f"   Départ: Centre Ville (-11.698, 43.256)")
    print(f"   Arrivée: Hôtel Itsandra (-11.655, 43.265)")
    print(f"   Prix: 180 KMF")
    print(f"   Statut: en_attente")
    
except Exception as e:
    print(f"❌ Erreur: {e}")

conn.close()