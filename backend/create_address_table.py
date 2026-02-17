# create_address_table.py
import sqlite3
import os

def create_address_table():
    db_path = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS adresses_frequentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        nom TEXT NOT NULL,               -- Ex: "Domicile", "Travail", "École"
        adresse TEXT NOT NULL,           -- Adresse complète
        latitude REAL,                   -- Coordonnées GPS
        longitude REAL,
        type TEXT DEFAULT 'personnel',   -- 'personnel', 'travail', 'famille'
        est_principale BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
    )
    ''')
    
    # Créer un index pour les recherches rapides
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_client_adresses ON adresses_frequentes(client_id)')
    
    conn.commit()
    conn.close()
    
    print("✅ Table 'adresses_frequentes' créée avec succès")

if __name__ == "__main__":
    create_address_table()