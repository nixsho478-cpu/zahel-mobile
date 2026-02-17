import sqlite3

print("=" * 60)
print("🔧 CORRECTION FINALE DU CONDUCTEUR ZH-327KYM")
print("=" * 60)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# AVANT
print("\n📊 ÉTAT AVANT CORRECTION :")
cursor.execute("SELECT disponible, en_course, courses_effectuees, gains_totaux FROM conducteurs WHERE immatricule='ZH-327KYM'")
dispo_avant, en_course_avant, courses_avant, gains_avant = cursor.fetchone()

print(f"  Disponible: {'OUI' if dispo_avant == 1 else 'NON'}")
print(f"  En course: {'OUI' if en_course_avant == 1 else 'NON'}")
print(f"  Courses effectuées: {courses_avant}")
print(f"  Gains totaux: {gains_avant} KMF")

# 1. Trouver et terminer les courses en cours
cursor.execute("""
    SELECT id, adresse_depart, adresse_arrivee, prix_convenu
    FROM courses 
    WHERE conducteur_id = (
        SELECT id FROM conducteurs WHERE immatricule='ZH-327KYM'
    )
    AND statut IN ('en_cours', 'acceptee')
""")

courses_en_cours = cursor.fetchall()
print(f"\n🚗 COURSES EN COURS TROUVÉES : {len(courses_en_cours)}")

for course in courses_en_cours:
    course_id, depart, arrivee, prix = course
    
    # Gérer les valeurs NULL
    depart_str = str(depart)[:20] + "..." if depart else "Adresse inconnue"
    arrivee_str = str(arrivee)[:20] + "..." if arrivee else "Adresse inconnue"
    
    print(f"  • Course ID {course_id}: {depart_str} → {arrivee_str} ({prix or 0} KMF)")
    
    # Terminer la course
    cursor.execute("UPDATE courses SET statut='terminee' WHERE id=?", (course_id,))
    print(f"    ✅ Terminée")

# 2. Libérer le conducteur
cursor.execute("UPDATE conducteurs SET disponible=1, en_course=0 WHERE immatricule='ZH-327KYM'")
print("\n✅ Conducteur ZH-327KYM libéré")

# 3. Recalculer les statistiques
# a) Nombre de courses terminées
cursor.execute("""
    SELECT COUNT(*) 
    FROM courses 
    WHERE conducteur_id = (
        SELECT id FROM conducteurs WHERE immatricule='ZH-327KYM'
    ) 
    AND statut = 'terminee'
""")
courses_terminees = cursor.fetchone()[0]

# b) Gains totaux
cursor.execute("""
    SELECT COALESCE(SUM(prix_convenu), 0)
    FROM courses 
    WHERE conducteur_id = (
        SELECT id FROM conducteurs WHERE immatricule='ZH-327KYM'
    ) 
    AND statut = 'terminee'
""")
gains_totaux = cursor.fetchone()[0]

# Mettre à jour les statistiques
cursor.execute("""
    UPDATE conducteurs 
    SET courses_effectuees = ?, 
        gains_totaux = ?
    WHERE immatricule = 'ZH-327KYM'
""", (courses_terminees, gains_totaux))

print(f"\n📈 Statistiques mises à jour:")
print(f"  • Courses effectuées: {courses_terminees}")
print(f"  • Gains totaux: {gains_totaux} KMF")

# APRÈS
print("\n📊 ÉTAT APRÈS CORRECTION :")
cursor.execute("SELECT disponible, en_course, courses_effectuees, gains_totaux FROM conducteurs WHERE immatricule='ZH-327KYM'")
dispo_apres, en_course_apres, courses_apres, gains_apres = cursor.fetchone()

print(f"  Disponible: {'OUI' if dispo_apres == 1 else 'NON'}")
print(f"  En course: {'OUI' if en_course_apres == 1 else 'NON'}")
print(f"  Courses effectuées: {courses_apres}")
print(f"  Gains totaux: {gains_apres} KMF")

conn.commit()
conn.close()

print("\n" + "=" * 60)
print("🎉 CORRECTION TERMINÉE AVEC SUCCÈS !")
print("=" * 60)
