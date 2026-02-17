import sqlite3

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

print("=== VÉRIFICATION RAPIDE ===")

# 1. Conducteur
cursor.execute("SELECT disponible, en_course FROM conducteurs WHERE immatricule='ZH-327KYM'")
dispo, en_course = cursor.fetchone()
print(f"ZH-327KYM - Disponible: {dispo}, En course: {en_course}")

# 2. Courses disponibles
cursor.execute("SELECT COUNT(*) FROM courses WHERE statut='en_attente' AND conducteur_id IS NULL")
courses_dispo = cursor.fetchone()[0]
print(f"Courses disponibles: {courses_dispo}")

# 3. Afficher quelques courses disponibles
cursor.execute("""
    SELECT code_unique, adresse_depart, adresse_arrivee, prix_convenu 
    FROM courses 
    WHERE statut='en_attente' 
    AND conducteur_id IS NULL
    LIMIT 3
""")
print(f"\n3 premières courses disponibles:")
for course in cursor.fetchall():
    code, depart, arrivee, prix = course
    depart_str = depart[:30] + "..." if depart and len(depart) > 30 else depart or "Inconnu"
    arrivee_str = arrivee[:30] + "..." if arrivee and len(arrivee) > 30 else arrivee or "Inconnu"
    print(f"  • {code}: {depart_str} → {arrivee_str} ({prix or 0} KMF)")

conn.close()
print("\n✅ Vérification terminée")
