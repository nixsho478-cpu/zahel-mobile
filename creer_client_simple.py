# creer_client_simple.py
import sqlite3
import hashlib

def hash_password(password):
    """Hash simple pour le test"""
    return hashlib.sha256(password.encode()).hexdigest()

print("🔐 CRÉATION CLIENT AVEC MOT DE PASSE SIMPLE")
print("="*50)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Client de test
telephone = "+26912345678"
nom = "Test Postman"
password = "test123"  # Mot de passe simple
password_hash = hash_password(password)

print(f"📱 Client: {telephone}")
print(f"🔑 Mot de passe: {password}")
print(f"🔐 Hash: {password_hash}")

# Vérifier si existe déjà
cursor.execute('SELECT id FROM clients WHERE telephone = ?', (telephone,))
if cursor.fetchone():
    print("ℹ️ Client existe déjà")
else:
    # Créer le client
    cursor.execute('''
        INSERT INTO clients (telephone, nom, password_hash)
        VALUES (?, ?, ?)
    ''', (telephone, nom, password_hash))
    
    conn.commit()
    print("✅ Client créé!")

conn.close()

print(f"\n🎯 TOKEN À UTILISER DANS POSTMAN:")
print(f"   Authorization: {password_hash}")
print(f"\n📝 POUR TESTER:")
print(f"   Téléphone: {telephone}")
print(f"   Mot de passe: {password}")
print(f"   Token (hash): {password_hash}")