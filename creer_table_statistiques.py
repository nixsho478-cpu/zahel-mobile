# creer_table_statistiques.py
import sqlite3

print("=" * 60)
print("📊 CRÉATION TABLE STATISTIQUES")
print("=" * 60)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Créer la table statistiques si elle n'existe pas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistiques (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        courses_jour INTEGER DEFAULT 0,
        revenus_jour DECIMAL DEFAULT 0,
        taxes_dues DECIMAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Vérifier si une ligne existe déjà
cursor.execute('SELECT COUNT(*) FROM statistiques')
count = cursor.fetchone()[0]

if count == 0:
    # Insérer une ligne initiale
    cursor.execute('INSERT INTO statistiques (id) VALUES (1)')
    print("✅ Ligne initiale insérée (id=1)")
else:
    print(f"✅ Table existe déjà avec {count} ligne(s)")

conn.commit()

# Vérification
cursor.execute('PRAGMA table_info(statistiques)')
columns = cursor.fetchall()
print("\n📋 Structure de la table 'statistiques':")
for col in columns:
    print(f"  {col[0]}: {col[1]} ({col[2]})")

conn.close()
print("\n🎉 Table statistiques prête !")