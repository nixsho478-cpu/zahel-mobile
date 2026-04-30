import sqlite3

conn = sqlite3.connect('zahel_secure.db')
cursor = conn.cursor()

# Voir les colonnes de la table conducteurs
cursor.execute("PRAGMA table_info(conducteurs)")
columns = cursor.fetchall()

print("\n=== COLONNES DE LA TABLE 'conducteurs' ===")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Vérifier spécifiquement latitude, longitude
col_names = [col[1] for col in columns]
print(f"\n✅ latitude présente: {'latitude' in col_names}")
print(f"✅ longitude présente: {'longitude' in col_names}")
print(f"✅ last_position_update présente: {'last_position_update' in col_names}")

conn.close()