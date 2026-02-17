# fixer_colonnes_clients.py
import sqlite3

print("🔧 CORRECTION TABLE CLIENTS - COLONNES MANQUANTES")
print("="*50)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Vérifier la structure actuelle
cursor.execute("PRAGMA table_info(clients)")
colonnes = cursor.fetchall()

print("📊 Structure actuelle de la table clients:")
col_names = [col[1] for col in colonnes]
for i, col in enumerate(colonnes):
    print(f"  {i}. {col[1]:20} {col[2]:15}")

# Colonnes nécessaires pour le système d'amendes
colonnes_necessaires = [
    ('avertissements_annulation', 'INTEGER DEFAULT 0'),
    ('amende_en_cours', 'REAL DEFAULT 0'),
    ('suspension_jusque', 'TIMESTAMP'),
    ('motif_suspension', 'TEXT')
]

print("\n🔍 Ajout des colonnes manquantes...")

for nom_col, type_col in colonnes_necessaires:
    if nom_col not in col_names:
        try:
            cursor.execute(f"ALTER TABLE clients ADD COLUMN {nom_col} {type_col}")
            print(f"✅ Colonne ajoutée: {nom_col} ({type_col})")
        except Exception as e:
            print(f"❌ Erreur avec {nom_col}: {e}")
    else:
        print(f"✅ Colonne déjà présente: {nom_col}")

# Vérifier aussi la table conducteurs
print("\n🚗 Vérification table conducteurs...")
cursor.execute("PRAGMA table_info(conducteurs)")
colonnes_cond = cursor.fetchall()

# Colonnes nécessaires pour conducteurs
colonnes_cond_necessaires = [
    ('courses_gratuites', 'INTEGER DEFAULT 0')
]

col_names_cond = [col[1] for col in colonnes_cond]
for nom_col, type_col in colonnes_cond_necessaires:
    if nom_col not in col_names_cond:
        try:
            cursor.execute(f"ALTER TABLE conducteurs ADD COLUMN {nom_col} {type_col}")
            print(f"✅ Colonne ajoutée à conducteurs: {nom_col}")
        except Exception as e:
            print(f"❌ Erreur avec {nom_col}: {e}")
    else:
        print(f"✅ Colonne déjà présente dans conducteurs: {nom_col}")

conn.commit()
conn.close()

print("\n✅ Correction terminée!")
print("Redémarrez le serveur pour prendre en compte les changements.")