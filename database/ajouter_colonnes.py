# ajouter_colonnes.py
import sqlite3

print("➕ AJOUT DES COLONNES MANQUANTES")
print("="*50)

conn = sqlite3.connect('zahel_secure.db')
cursor = conn.cursor()

# Colonnes à ajouter
colonnes = [
    ('amendes_dues', 'REAL DEFAULT 0'),
    ('amendes_payees', 'REAL DEFAULT 0'),
    ('taxes_payees', 'REAL DEFAULT 0')  # Elle manque aussi probablement
]

for nom_col, type_col in colonnes:
    try:
        # Vérifier si la colonne existe déjà
        cursor.execute(f"SELECT {nom_col} FROM statistiques LIMIT 1")
        print(f"✅ {nom_col}: existe déjà")
    except:
        # Ajouter la colonne
        try:
            cursor.execute(f"ALTER TABLE statistiques ADD COLUMN {nom_col} {type_col}")
            print(f"➕ {nom_col}: ajoutée")
        except Exception as e:
            print(f"❌ {nom_col}: erreur - {e}")

conn.commit()

# Vérifier
cursor.execute("PRAGMA table_info(statistiques)")
cols = cursor.fetchall()
print(f"\n📋 {len(cols)} colonnes au total:")
for col in cols:
    print(f"  {col[0]:2}. {col[1]:25} {col[2]:15}")

conn.close()
print("\n🎉 Colonnes ajoutées!")