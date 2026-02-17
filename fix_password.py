# fix_password.py
import hashlib
import sqlite3

print("🔄 Réinitialisation du mot de passe ZH-327KYM...")

# Connexion à la base
conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Vérifier si le conducteur existe
cursor.execute("SELECT immatricule, nom FROM conducteurs WHERE immatricule = 'ZH-327KYM'")
row = cursor.fetchone()

if not row:
    print("❌ Conducteur ZH-327KYM non trouvé")
else:
    print(f"✅ Conducteur trouvé: {row[0]} - {row[1]}")
    
    # Générer le hash SHA256 (comme dans api_zahel.py)
    password = "zahel123"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    print(f"🔐 Nouveau hash SHA256 généré:")
    print(f"   {password_hash}")
    
    # Mettre à jour la base
    cursor.execute("UPDATE conducteurs SET password_hash = ? WHERE immatricule = ?",
                   (password_hash, 'ZH-327KYM'))
    
    conn.commit()
    print("✅ Mot de passe mis à jour dans la base de données")

conn.close()
print("🎯 Terminé !")