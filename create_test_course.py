import sqlite3
import datetime
import random
import string

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

print("🔍 Vérification de la structure de la table 'courses'...")
cursor.execute("PRAGMA table_info(courses)")
columns = cursor.fetchall()

print("\n📊 STRUCTURE DE LA TABLE COURSES:")
print("=" * 50)
for col in columns:
    col_name = col[1]
    col_type = col[2]
    not_null = "NOT NULL" if col[3] else "NULL"
    print(f"{col_name:25} {col_type:15} {not_null}")

# Chercher la colonne pour le code
code_column = None
for col in columns:
    if 'code' in col[1].lower():
        code_column = col[1]
        break

print(f"\n🔍 Colonne code trouvée: {code_column}")

# Créer une course test
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
test_code = 'TEST-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

try:
    if code_column:
        # Avec colonne code
        cursor.execute(f'''
            INSERT INTO courses (
                {code_column}, client_id, conducteur_id,
                depart_lat, depart_lng, arrivee_lat, arrivee_lng,
                prix_convenu, statut, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            test_code, 3, None,  # client_id=3, conducteur_id=NULL
            -11.698, 43.256, -11.655, 43.265,  # Centre Ville -> Hôtel Itsandra
            150, 'en_attente', now
        ))
    else:
        # Sans colonne code
        cursor.execute('''
            INSERT INTO courses (
                client_id, conducteur_id,
                depart_lat, depart_lng, arrivee_lat, arrivee_lng,
                prix_convenu, statut, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            3, None,  # client_id=3, conducteur_id=NULL
            -11.698, 43.256, -11.655, 43.265,  # Centre Ville -> Hôtel Itsandra
            150, 'en_attente', now
        ))
    
    conn.commit()
    course_id = cursor.lastrowid
    
    print(f"\n✅ COURSE TEST CRÉÉE AVEC SUCCÈS!")
    print(f"   ID: {course_id}")
    if code_column:
        print(f"   Code: {test_code}")
    print(f"   Départ: Centre Ville Moroni (-11.698, 43.256)")
    print(f"   Arrivée: Hôtel Itsandra (-11.655, 43.265)")
    print(f"   Prix: 150 KMF")
    print(f"   Statut: en_attente")
    print(f"   Conducteur: AUCUN (disponible pour acceptation)")
    
    # Vérifier qu'elle est bien disponible
    cursor.execute('''
        SELECT COUNT(*) FROM courses 
        WHERE statut = 'en_attente' AND conducteur_id IS NULL
    ''')
    count = cursor.fetchone()[0]
    print(f"\n📊 Courses disponibles sans conducteur: {count}")
    
except Exception as e:
    print(f"\n❌ Erreur lors de la création: {e}")
    print("\n🔄 Tentative alternative...")
    
    # Voir ce qu'il y a déjà dans la table
    cursor.execute("SELECT * FROM courses LIMIT 1")
    sample = cursor.fetchone()
    if sample:
        print("\n📋 Exemple de course existante:")
        for i, col in enumerate(columns):
            if i < len(sample):
                print(f"   {col[1]}: {sample[i]}")

conn.close()