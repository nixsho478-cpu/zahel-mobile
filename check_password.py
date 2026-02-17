import sqlite3

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# 1. Vérifier le conducteur ZH-327KYM
cursor.execute('SELECT immatricule, password_hash FROM conducteurs WHERE immatricule="ZH-327KYM"')
result = cursor.fetchone()

print('🔍 CONDUCTEUR ZH-327KYM:')
if result:
    print(f'   ✅ Trouvé: {result[0]}')
    print(f'   🔐 Password_hash: "{result[1]}"')
    print(f'   📏 Longueur: {len(result[1])} caractères')
    
    # Vérifier si c'est un hash MD5 (32 caractères hexa)
    if len(result[1]) == 32 and all(c in '0123456789abcdef' for c in result[1].lower()):
        print(f'   🎯 Type: HASH MD5')
    else:
        print(f'   🎯 Type: TEXTE CLAIR')
else:
    print('   ❌ Non trouvé!')

print()
print('🔍 TOUS LES CONDUCTEURS (pour debug):')
cursor.execute('SELECT immatricule, password_hash FROM conducteurs')
for row in cursor.fetchall():
    print(f'   {row[0]} -> "{row[1]}"')

conn.close()