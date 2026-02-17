# debug_course_luxe_detailed.py
import sqlite3
import json

print("🔍 DEBUG DÉTAILLÉ COURSE LUXE ZAHEL-AWN7383")
print("============================================")

db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Vérifier la course spécifique
print("1. 📊 INFOS COURSE ZAHEL-AWN7383")
cursor.execute("""
    SELECT code_unique, categorie_demande, statut, 
           timer_luxe_demarre_le, date_debut_recherche_luxe,
           prix_convenu, client_id
    FROM courses 
    WHERE code_unique = 'ZAHEL-AWN7383'
""")

course = cursor.fetchone()
if course:
    print(f"✅ Course trouvée:")
    print(f"   Code: {course[0]}")
    print(f"   Catégorie: {course[1]}")
    print(f"   Statut: {course[2]}")
    print(f"   Timer luxe démarré: {course[3]}")
    print(f"   Date début recherche luxe: {course[4]}")
    print(f"   Prix: {course[5]} KMF")
    print(f"   Client ID: {course[6]}")
else:
    print("❌ Course non trouvée dans la base")

# 2. Vérifier les 5 dernières courses
print("\n2. 📅 5 DERNIÈRES COURSES")
cursor.execute("""
    SELECT code_unique, categorie_demande, statut, date_demande
    FROM courses 
    ORDER BY date_demande DESC 
    LIMIT 5
""")

courses = cursor.fetchall()
for c in courses:
    print(f"   • {c[0]}: {c[1]} ({c[2]}) - {c[3]}")

# 3. Vérifier la configuration timeout luxe
print("\n3. ⚙️ CONFIGURATION TIMER LUXE")
cursor.execute("SELECT valeur FROM configurations WHERE cle='timeout_recherche_luxe'")
config = cursor.fetchone()
print(f"   Timeout recherche luxe: {config[0] if config else 'Non configuré'} secondes")

# 4. Vérifier la fonction API check_luxe_timeout
print("\n4. 🛠️ ANALYSE FONCTION check_luxe_timeout")
print("   (Vérifie dans api_zahel.py la logique de cette fonction)")

conn.close()

print("\n============================================")
print("INSTRUCTIONS:")
print("1. Vérifie que categorie_demande = 'luxe' pour ZAHEL-AWN7383")
print("2. Si non, vérifie la fonction demander_course() dans api_zahel.py")
print("3. Si oui, vérifie la fonction check_luxe_timeout()")