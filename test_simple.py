# test_simple.py
import sqlite3

print("=== TEST SIMPLE CONDUCTEURS ===")

# Connexion
conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# 1. Tous les conducteurs
print("\n1. TOUS LES CONDUCTEURS:")
cursor.execute("SELECT immatricule, nom FROM conducteurs")
all_drivers = cursor.fetchall()
print(f"Total: {len(all_drivers)}")
for d in all_drivers:
    print(f"  • {d[0]}: {d[1]}")

# 2. ZH-327KYM détaillé
print("\n2. ZH-327KYM DÉTAILLÉ:")
cursor.execute("""
    SELECT immatricule, nom, 
           compte_active, disponible, en_course, compte_suspendu,
           latitude, longitude
    FROM conducteurs 
    WHERE immatricule='ZH-327KYM'
""")
driver = cursor.fetchone()

if driver:
    print(f"Immatricule: {driver[0]}")
    print(f"Nom: {driver[1]}")
    print(f"compte_active: {driver[2]} (type: {type(driver[2])})")
    print(f"disponible: {driver[3]} (type: {type(driver[3])})")
    print(f"en_course: {driver[4]} (type: {type(driver[4])})")
    print(f"compte_suspendu: {driver[5]} (type: {type(driver[5])})")
    print(f"Position: {driver[6]}, {driver[7]}")
else:
    print("❌ Conducteur non trouvé!")

# 3. Test de la requête API
print("\n3. TEST REQUÊTE API (même conditions):")
query = """
SELECT immatricule, nom 
FROM conducteurs 
WHERE compte_active = 1
  AND disponible = 1
  AND en_course = 0
  AND compte_suspendu = 0
  AND (latitude BETWEEN ? AND ?)
  AND (longitude BETWEEN ? AND ?)
"""
params = [-11.7433, -11.6533, 43.2100, 43.3020]

cursor.execute(query, params)
results = cursor.fetchall()
print(f"Trouvés: {len(results)}")
for r in results:
    print(f"  • {r[0]}: {r[1]}")

conn.close()
print("\n=== FIN TEST ===")