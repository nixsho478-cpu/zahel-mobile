import sqlite3

print("=== VÉRIFICATION CONDUCTEUR ZH-327KYM ===")

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# État du conducteur
cursor.execute("SELECT disponible, en_course, total_courses, revenus_totaux FROM conducteurs WHERE immatricule='ZH-327KYM'")
dispo, en_course, total, revenus = cursor.fetchone()

print(f"1. Disponible: {'OUI' if dispo == 1 else 'NON'}")
print(f"2. En course: {'OUI' if en_course == 1 else 'NON'}")
print(f"3. Total courses: {total}")
print(f"4. Revenus totaux: {revenus} KMF")

# Courses du conducteur
cursor.execute("""
    SELECT code, statut, prix_convenu 
    FROM courses 
    WHERE conducteur_id = (
        SELECT id FROM conducteurs WHERE immatricule='ZH-327KYM'
    ) 
    ORDER BY created_at DESC 
    LIMIT 5
""")

print("\n=== 5 DERNIÈRES COURSES ===")
for course in cursor.fetchall():
    print(f"- {course[0]}: {course[1]} ({course[2]} KMF)")

conn.close()
print("\n✅ Vérification terminée")
