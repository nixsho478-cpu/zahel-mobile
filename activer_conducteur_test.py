# activer_conducteur_test.py
import sqlite3

print("🚗 ACTIVATION CONDUCTEUR POUR TEST")
print("="*50)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Prendre le premier conducteur (ZH-327KYM)
cursor.execute('''
    UPDATE conducteurs 
    SET disponible = 1, 
        compte_active = 1,
        compte_suspendu = 0,
        compte_bloque = 0,
        en_course = 0
    WHERE immatricule = 'ZH-327KYM'
''')

updated = cursor.rowcount
conn.commit()

if updated > 0:
    print("✅ Conducteur ZH-327KYM activé pour les tests!")
    print("Il peut maintenant accepter des courses.")
else:
    print("⚠️ Conducteur ZH-327KYM non trouvé")

# Vérifier
cursor.execute('''
    SELECT immatricule, nom, disponible, compte_active 
    FROM conducteurs WHERE immatricule = 'ZH-327KYM'
''')
cond = cursor.fetchone()

if cond:
    print(f"\n📋 État après activation:")
    print(f"  Immatricule: {cond[0]}")
    print(f"  Nom: {cond[1]}")
    print(f"  Disponible: {'✅ Oui' if cond[2] == 1 else '❌ Non'}")
    print(f"  Compte actif: {'✅ Oui' if cond[3] == 1 else '❌ Non'}")

conn.close()