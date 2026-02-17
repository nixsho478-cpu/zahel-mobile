# reset_password.py
import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

print("🔍 Recherche du conducteur ZH-327KYM...")
cursor.execute("SELECT immatricule, nom FROM conducteurs WHERE immatricule = 'ZH-327KYM'")
row = cursor.fetchone()

if not row:
    print('❌ Conducteur ZH-327KYM non trouvé')
else:
    print(f'✅ Conducteur trouvé: {row[0]} - {row[1]}')
    
    # Créer un nouveau mot de passe
    nouveau_password = 'zahel123'
    password_hash = generate_password_hash(nouveau_password)
    
    # Mettre à jour
    cursor.execute('UPDATE conducteurs SET password_hash = ? WHERE immatricule = ?', 
                   (password_hash, 'ZH-327KYM'))
    
    print(f'✅ Mot de passe réinitialisé')
    print(f'   Nouveau mot de passe: {nouveau_password}')
    
    conn.commit()
    print('✅ Base de données mise à jour')

conn.close()