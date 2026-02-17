# fix_courses.py
import sqlite3

print("=" * 50)
print("🔧 CORRECTION DES COURSES EXISTANTES")
print("=" * 50)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# 1. Voir toutes les colonnes de la table courses
cursor.execute("PRAGMA table_info(courses)")
columns = [col[1] for col in cursor.fetchall()]
print("📋 Colonnes de la table 'courses':")
print(f"   {', '.join(columns)}")

# 2. Voir les courses en attente
cursor.execute("SELECT code_unique, statut, conducteur_id FROM courses WHERE statut LIKE '%attente%' OR statut LIKE '%recherche%'")
courses = cursor.fetchall()

print(f"\n📦 {len(courses)} course(s) en attente/recherche:")
for course in courses:
    status = "✅ Libre" if not course[2] else f"❌ Attribuée à {course[2]}"
    print(f"   • {course[0]} - {course[1]} - {status}")

# 3. Désattribuer les courses
if courses:
    print("\n🔄 Désattribution des courses...")
    # Compter combien sont attribuées
    cursor.execute("SELECT COUNT(*) FROM courses WHERE conducteur_id IS NOT NULL AND statut IN ('en_attente', 'en_recherche')")
    count_attribuees = cursor.fetchone()[0]
    
    if count_attribuees > 0:
        cursor.execute("UPDATE courses SET conducteur_id = NULL WHERE statut IN ('en_attente', 'en_recherche') AND conducteur_id IS NOT NULL")
        updated = cursor.rowcount
        conn.commit()
        print(f"✅ {updated} course(s) désattribuée(s)")
    else:
        print("✅ Aucune course à désattribuer")

# 4. Vérifier après correction
cursor.execute("SELECT COUNT(*) FROM courses WHERE statut IN ('en_attente', 'en_recherche') AND conducteur_id IS NULL")
libres = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM courses WHERE statut IN ('en_attente', 'en_recherche')")
total = cursor.fetchone()[0]

print(f"\n📊 STATUT FINAL:")
print(f"   • Courses totales en attente: {total}")
print(f"   • Courses non attribuées: {libres}")
print(f"   • Courses attribuées: {total - libres}")

conn.close()

print("\n" + "=" * 50)
print("🎯 Maintenant, testez /api/courses/disponibles !")
input("Appuyez sur ENTREE pour continuer...")