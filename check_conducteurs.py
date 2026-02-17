# check_conducteurs.py
import sqlite3
import os

db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"
print(f"📁 Chemin DB: {db_path}")
print(f"📁 Existe: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Vérifier TOUS les conducteurs
cursor.execute('''
    SELECT id, immatricule, nom, disponible, en_course, 
           compte_active, compte_suspendu, en_attente_verification,
           latitude, longitude
    FROM conducteurs
    ORDER BY disponible DESC, en_course ASC
''')

print("\n" + "="*80)
print("📊 ÉTAT COMPLET DES CONDUCTEURS")
print("="*80)

for row in cursor.fetchall():
    id_, immatricule, nom, disponible, en_course, compte_active, compte_suspendu, en_attente, lat, lng = row
    
    status = []
    if disponible == 1: status.append("✅ DISPONIBLE")
    else: status.append("❌ INDISPONIBLE")
    
    if en_course == 1: status.append("🚗 EN COURSE")
    if compte_active == 0: status.append("🚫 COMPTE INACTIF")
    if compte_suspendu == 1: status.append("⏸️ SUSPENDU")
    if en_attente == 1: status.append("⏳ EN ATTENTE VÉRIFICATION")
    
    print(f"\n👤 {nom} ({immatricule}) - ID: {id_}")
    print(f"   Statut: {', '.join(status)}")
    print(f"   Position: ({lat}, {lng})")
    
    # Vérifier s'il passe les filtres de l'API
    filters_ok = all([
        disponible == 1,
        en_course == 0,
        compte_active == 1,
        compte_suspendu == 0
    ])
    
    if filters_ok:
        print(f"   ✅ Passe les filtres API")
    else:
        print(f"   ❌ Ne passe pas les filtres API")

conn.close()

print("\n" + "="*80)
print("🎯 Test de la requête API exacte :")
print("="*80)

# Test de la requête exacte que fait l'API
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

lat = -11.704
lng = 43.2605
radius = 5

# Approximation rapide (1 degré ≈ 111 km)
lat_range = radius / 111.0
lng_range = radius / (111.0 * abs(cos(radians(lat))))

query = '''
SELECT immatricule, nom, latitude, longitude
FROM conducteurs 
WHERE compte_active = 1 
    AND disponible = 1 
    AND en_course = 0
    AND compte_suspendu = 0
    AND (
        (latitude BETWEEN ? AND ?)
        AND (longitude BETWEEN ? AND ?)
    )
LIMIT 10
'''

params = [lat - lat_range, lat + lat_range, lng - lng_range, lng + lng_range]

print(f"🔍 Requête: {query}")
print(f"🔍 Paramètres: {params}")

try:
    from math import cos, radians
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    if results:
        print(f"✅ {len(results)} conducteur(s) trouvé(s) dans le rayon:")
        for r in results:
            print(f"   - {r[1]} ({r[0]}) à ({r[2]}, {r[3]})")
    else:
        print("❌ Aucun conducteur trouvé avec ces filtres")
        
        # Vérifier sans le filtre de distance
        cursor.execute('''
            SELECT immatricule, nom, latitude, longitude
            FROM conducteurs 
            WHERE compte_active = 1 
                AND disponible = 1 
                AND en_course = 0
                AND compte_suspendu = 0
        ''')
        all_available = cursor.fetchall()
        
        if all_available:
            print(f"\n📌 Mais il y a {len(all_available)} conducteur(s) disponible(s) sans filtre distance:")
            for r in all_available:
                print(f"   - {r[1]} ({r[0]}) à ({r[2]}, {r[3]})")
                
                # Calculer la distance approximative
                dist_lat = abs(r[2] - lat) * 111.0  # km
                dist_lng = abs(r[3] - lng) * 111.0 * abs(cos(radians(lat)))
                dist = (dist_lat**2 + dist_lng**2)**0.5
                print(f"     Distance: {dist:.1f} km")
                
except Exception as e:
    print(f"💥 Erreur: {e}")

conn.close()