# creer_amende_test.py
import sqlite3
import datetime

db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"

print("🛠️ CRÉATION D'UNE AMENDE DE TEST")
print("=" * 40)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Trouver le client test
cursor.execute("SELECT id, telephone, nom FROM clients WHERE telephone = ?", ("+26934011111",))
client = cursor.fetchone()

if client:
    print(f"✅ Client trouvé: {client[2]} ({client[1]})")
    
    # 2. Créer une amende
    amende_data = (
        client[0],  # client_id
        500,        # montant (500 KMF)
        "annulation_tardive - Test système ZAHEL",
        "client",   # utilisateur_type
        "en_attente", # statut
        datetime.datetime.now().isoformat(),  # date_amende
        None,       # date_paiement
        datetime.datetime.now().isoformat()   # created_at
    )
    
    cursor.execute('''
        INSERT INTO amendes 
        (utilisateur_id, montant, raison, utilisateur_type, statut, date_amende, date_paiement, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', amende_data)
    
    conn.commit()
    print("✅ Amende de test créée : 500 KMF")
    print("   Raison : annulation_tardive - Test système ZAHEL")
    
else:
    print("❌ Client +26934011111 non trouvé")

conn.close()

print("\n" + "=" * 40)
print("TEST TERMINÉ")
print("=" * 40)
input("Appuie sur ENTRÉE pour quitter...")