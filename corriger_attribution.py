# corriger_attribution.py
import sqlite3

print("=" * 50)
print("🔧 CORRECTION DE L'ATTRIBUTION AUTOMATIQUE")
print("=" * 50)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# 1. Vérifier les courses en attente
cursor.execute('''
    SELECT id, code_unique, conducteur_id 
    FROM courses 
    WHERE statut = "en_attente" 
    ORDER BY created_at DESC
''')
courses = cursor.fetchall()

print(f"📋 {len(courses)} course(s) en attente:")
for course in courses:
    print(f"  • {course[1]} - Conducteur ID: {course[2] if course[2] else 'NULL'}")

# 2. Retirer l'attribution automatique (mettre conducteur_id à NULL)
if courses:
    print("\n🔄 Retrait de l'attribution automatique...")
    cursor.execute('''
        UPDATE courses 
        SET conducteur_id = NULL 
        WHERE statut = "en_attente" 
        AND conducteur_id IS NOT NULL
    ''')
    updated = cursor.rowcount
    conn.commit()
    print(f"✅ {updated} course(s) corrigée(s)")
else:
    print("\n✅ Aucune course à corriger")

# 3. Vérifier après correction
cursor.execute('''
    SELECT code_unique, conducteur_id 
    FROM courses 
    WHERE statut = "en_attente"
''')
courses_after = cursor.fetchall()

print("\n📊 APRÈS CORRECTION:")
for course in courses_after:
    status = "✅ Non attribuée" if not course[1] else "❌ Toujours attribuée"
    print(f"  • {course[0]} - {status}")

conn.close()

print("\n" + "=" * 50)
print("🎯 Maintenant, rafraîchissez l'app Kivy !")
input("Appuyez sur ENTREE pour continuer...")