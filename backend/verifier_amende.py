# verifier_amende.py
import sqlite3
import json

db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Vérifier la course ZAHEL-UVE4453
cursor.execute('''
SELECT code_unique, amende_incluse, montant_amende, amendes_ids, prix_convenu
FROM courses 
WHERE code_unique = 'ZAHEL-UVE4453'
''')

course = cursor.fetchone()

if course:
    print("✅ COURSE TROUVÉE DANS LA BASE DE DONNÉES")
    print(f"📝 Code: {course[0]}")
    print(f"📊 Amende incluse: {'OUI' if course[1] else 'NON'}")
    print(f"💰 Montant amende: {course[2]} KMF")
    print(f"🆔 IDs amendes: {course[3]}")
    print(f"💵 Prix convenu: {course[4]} KMF")
    
    # Calculer le prix total
    prix_total = course[4] + (course[2] or 0)
    print(f"💵 Prix total calculé: {prix_total} KMF")
    
    # Afficher le JSON de l'amende si présent
    if course[1]:
        try:
            amende_data = json.loads(course[1])
            print(f"📋 Détails amende JSON: {json.dumps(amende_data, indent=2)}")
        except:
            print("⚠️  Impossible de parser JSON amende")
else:
    print("❌ Course non trouvée")

conn.close()