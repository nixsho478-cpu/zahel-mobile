# check_client_details.py
import sqlite3
import hashlib

print("🔍 VÉRIFICATION DÉTAILLÉE DU CLIENT")
print("="*50)

def hash_password(password):
    """Même fonction de hash que dans api_zahel.py"""
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Chercher le client +26934011111
telephone = "+26934011111"
cursor.execute("SELECT id, telephone, nom, password_hash FROM clients WHERE telephone = ?", (telephone,))
client = cursor.fetchone()

if client:
    print(f"✅ Client trouvé dans la base:")
    print(f"   ID: {client[0]}")
    print(f"   Téléphone: {client[1]}")
    print(f"   Nom: {client[2]}")
    print(f"   Password hash: {client[3]}")
    
    # Tester différents mots de passe possibles
    print("\n🔐 Test des mots de passe courants:")
    test_passwords = ["test123", "password", "zahel", "123456", "test", ""]
    
    for pwd in test_passwords:
        hashed = hash_password(pwd)
        if hashed == client[3]:
            print(f"   ✅ Mot de passe trouvé: '{pwd}'")
            break
    else:
        print("   ❌ Aucun mot de passe testé ne correspond")
        print(f"   Hash dans la base: {client[3]}")
        
else:
    print(f"❌ Client {telephone} non trouvé dans la base")

conn.close()