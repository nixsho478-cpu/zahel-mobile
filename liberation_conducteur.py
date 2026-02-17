# liberation_conducteur.py
import sqlite3

print("=== LIBÉRATION CONDUCTEUR ZH-327KYM ===")

# Connexion à la base
conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# État actuel
cursor.execute("SELECT immatricule, nom, disponible, en_course FROM conducteurs WHERE immatricule='ZH-327KYM'")
driver = cursor.fetchone()

if driver:
    print(f"Avant: {driver[0]} - {driver[1]}")
    print(f"  Disponible: {driver[2]} (doit être 1)")
    print(f"  En course: {driver[3]} (doit être 0)")
    
    # Libérer le conducteur
    cursor.execute("UPDATE conducteurs SET en_course=0, disponible=1 WHERE immatricule='ZH-327KYM'")
    conn.commit()
    print("✅ Conducteur libéré")
    
    # Vérifier
    cursor.execute("SELECT disponible, en_course FROM conducteurs WHERE immatricule='ZH-327KYM'")
    result = cursor.fetchone()
    print(f"Après: disponible={result[0]}, en_course={result[1]}")
else:
    print("❌ Conducteur non trouvé")

conn.close()
print("=== FIN ===")