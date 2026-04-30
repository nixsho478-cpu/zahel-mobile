# create_missing_tables.py
import sqlite3

db_path = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Notifications conducteur
cursor.execute('''
CREATE TABLE IF NOT EXISTS notifications_conducteur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conducteur_id INTEGER NOT NULL,
    course_code TEXT,
    type_notification TEXT DEFAULT 'nouvelle_course',
    message TEXT,
    lue INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
print("✅ Table 'notifications_conducteur' créée")

# 2. Logs sécurité
cursor.execute('''
CREATE TABLE IF NOT EXISTS logs_securite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    utilisateur_type TEXT,
    utilisateur_id INTEGER,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
print("✅ Table 'logs_securite' créée")

# 3. Statistiques
cursor.execute('''
CREATE TABLE IF NOT EXISTS statistiques (
    id INTEGER PRIMARY KEY,
    courses_jour INTEGER DEFAULT 0,
    revenus_jour DECIMAL(10,2) DEFAULT 0,
    taxes_dues DECIMAL(10,2) DEFAULT 0,
    amendes_dues DECIMAL(10,2) DEFAULT 0,
    amendes_payees DECIMAL(10,2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
cursor.execute("INSERT OR IGNORE INTO statistiques (id) VALUES (1)")
print("✅ Table 'statistiques' créée")

conn.commit()
conn.close()
print("\n🎉 Toutes les tables sont prêtes !")