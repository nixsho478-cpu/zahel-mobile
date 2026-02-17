# fix_courses_table.py
import sqlite3

print("🔧 CORRECTION TABLE COURSES")
print("="*50)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Vérifier la structure actuelle
cursor.execute("PRAGMA table_info(courses)")
colonnes = cursor.fetchall()

print("📊 Structure actuelle de la table courses:")
col_names = [col[1] for col in colonnes]
for i, col in enumerate(colonnes):
    print(f"  {i}. {col[1]:25} {col[2]:15}")

# Colonnes nécessaires pour le système d'annulation
colonnes_necessaires = [
    ('motif_annulation', 'TEXT'),
    ('annule_par', 'TEXT'),  # 'client' ou 'conducteur'
    ('taxes_zahel', 'REAL DEFAULT 0'),
    ('paiement_effectue', 'BOOLEAN DEFAULT 0')
]

print("\n🔍 Ajout des colonnes manquantes...")

for nom_col, type_col in colonnes_necessaires:
    if nom_col not in col_names:
        try:
            cursor.execute(f"ALTER TABLE courses ADD COLUMN {nom_col} {type_col}")
            print(f"✅ Colonne ajoutée: {nom_col} ({type_col})")
        except Exception as e:
            print(f"❌ Erreur avec {nom_col}: {e}")
    else:
        print(f"✅ Colonne déjà présente: {nom_col}")

# Vérifier aussi d'autres tables importantes
tables_a_verifier = ['amendes', 'avertissements', 'suspensions']
for table in tables_a_verifier:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"✅ Table {table}: {count} enregistrement(s)")
    except:
        print(f"⚠️ Table {table} non accessible ou n'existe pas")

conn.commit()
conn.close()

print("\n✅ Correction terminée!")
print("Redémarrez le serveur pour prendre en compte les changements.")