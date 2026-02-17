import sqlite3

print("=== CORRECTION CONDUCTEUR ZH-327KYM ===")

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Avant
cursor.execute("SELECT disponible, en_course FROM conducteurs WHERE immatricule='ZH-327KYM'")
dispo_avant, en_course_avant = cursor.fetchone()
print(f"AVANT: Disponible={dispo_avant}, En course={en_course_avant}")

# 1. Terminer toutes les courses en cours
cursor.execute("""
    UPDATE courses 
    SET statut = 'terminee' 
    WHERE conducteur_id = (
        SELECT id FROM conducteurs WHERE immatricule='ZH-327KYM'
    ) 
    AND statut IN ('en_cours', 'acceptee')
""")
courses_corrigees = cursor.rowcount
print(f"\n✅ {courses_corrigees} course(s) terminée(s)")

# 2. Libérer le conducteur
cursor.execute("UPDATE conducteurs SET disponible=1, en_course=0 WHERE immatricule='ZH-327KYM'")
print("✅ Conducteur libéré")

# 3. Recalculer les statistiques
cursor.execute("""
    UPDATE conducteurs 
    SET total_courses = (
        SELECT COUNT(*) FROM courses 
        WHERE conducteur_id = conducteurs.id 
        AND statut = 'terminee'
    ),
    revenus_totaux = (
        SELECT COALESCE(SUM(prix_convenu), 0) FROM courses 
        WHERE conducteur_id = conducteurs.id 
        AND statut = 'terminee'
    )
    WHERE immatricule = 'ZH-327KYM'
""")
print("✅ Statistiques recalculées")

# Après
cursor.execute("SELECT disponible, en_course, total_courses, revenus_totaux FROM conducteurs WHERE immatricule='ZH-327KYM'")
dispo_apres, en_course_apres, total, revenus = cursor.fetchone()
print(f"\nAPRÈS: Disponible={dispo_apres}, En course={en_course_apres}")
print(f"Total courses: {total}")
print(f"Revenus totaux: {revenus} KMF")

conn.commit()
conn.close()

print("\n🎉 Correction terminée avec succès !")
