# check_conducteurs_dispo.py
import sqlite3

print("🚗 VÉRIFICATION CONDUCTEURS DISPONIBLES")
print("="*50)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Vérifier tous les conducteurs
cursor.execute('''
    SELECT id, immatricule, nom, disponible, compte_active, 
           compte_suspendu, compte_bloque, en_attente_verification
    FROM conducteurs
''')

conducteurs = cursor.fetchall()

print(f"👥 {len(conducteurs)} conducteur(s) trouvé(s):")
print("-"*80)

for cond in conducteurs:
    status = []
    if cond[3] == 1: 
        status.append("✅ Disponible")
    else: 
        status.append("❌ Non disponible")
    
    if cond[4] == 1: 
        status.append("✅ Compte actif")
    else: 
        status.append("❌ Compte inactif")
    
    if cond[5] == 1: 
        status.append("❌ Suspendu")
    if cond[6] == 1: 
        status.append("❌ Bloqué")
    if cond[7] == 1: 
        status.append("⚠️ En attente vérification")
    
    print(f"  {cond[1]} - {cond[2]}")
    print(f"    Statut: {', '.join(status)}")
    print()

# Vérifier qui pourrait accepter une course
cursor.execute('''
    SELECT immatricule, nom FROM conducteurs 
    WHERE disponible = 1 
      AND compte_active = 1 
      AND compte_suspendu = 0 
      AND compte_bloque = 0
''')

disponibles = cursor.fetchall()

if disponibles:
    print("🚗 CONDUCTEURS DISPONIBLES POUR ACCEPTER UNE COURSE:")
    for cond in disponibles:
        print(f"  ✅ {cond[0]} - {cond[1]}")
else:
    print("⚠️ AUCUN CONDUCTEUR DISPONIBLE")
    print("Les conducteurs doivent être:")
    print("  - disponible = 1")
    print("  - compte_active = 1")
    print("  - compte_suspendu = 0")
    print("  - compte_bloque = 0")

conn.close()