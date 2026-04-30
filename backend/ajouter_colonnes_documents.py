# ajouter_colonnes_documents.py
import sqlite3

db_path = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Vérifier les colonnes existantes
cursor.execute("PRAGMA table_info(conducteurs)")
colonnes = [col[1] for col in cursor.fetchall()]

colonnes_a_ajouter = [
    ('permis_valide', 'INTEGER DEFAULT 0'),
    ('assurance_valide', 'INTEGER DEFAULT 0'),
    ('carte_grise_valide', 'INTEGER DEFAULT 0'),
    ('photo_permis', 'TEXT'),
    ('photo_identite', 'TEXT'),
    ('photo_carte_grise', 'TEXT'),
    ('photo_vehicule', 'TEXT'),
    ('date_expiration_permis', 'DATE'),
    ('date_expiration_assurance', 'DATE'),
    ('numero_licence', 'TEXT')
]

for col_name, col_type in colonnes_a_ajouter:
    if col_name not in colonnes:
        try:
            cursor.execute(f"ALTER TABLE conducteurs ADD COLUMN {col_name} {col_type}")
            print(f"✅ Colonne '{col_name}' ajoutée")
        except Exception as e:
            print(f"⚠️ Erreur ajout {col_name}: {e}")

conn.commit()
conn.close()
print("✅ Mise à jour de la base de données terminée")