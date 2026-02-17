# fix_columns_complete.py
import sqlite3
import os

print("🔧 AJOUT DES COLONNES MANQUANTES POUR TIMER LUXE")
print("================================================")

db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"

# Se connecter
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Liste des colonnes à ajouter
columns_to_add = [
    ('timer_luxe_demarre_le', 'TIMESTAMP'),
    ('date_debut_recherche_luxe', 'TIMESTAMP')
]

# Vérifier les colonnes existantes
cursor.execute("PRAGMA table_info(courses)")
existing_columns = [col[1] for col in cursor.fetchall()]
print("Colonnes existantes vérifiées")

# Ajouter les colonnes manquantes
for column_name, column_type in columns_to_add:
    if column_name not in existing_columns:
        print(f"\nAjout de la colonne: {column_name} ({column_type})")
        try:
            cursor.execute(f"ALTER TABLE courses ADD COLUMN {column_name} {column_type}")
            print(f"✅ {column_name} ajoutée avec succès")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    else:
        print(f"\n✅ {column_name} existe déjà")

# Vérifier la table mise à jour
print("\n=== STRUCTURE FINALE DE LA TABLE COURSES ===")
cursor.execute("PRAGMA table_info(courses)")
for col in cursor.fetchall():
    print(f"{col[1]:30} ({col[2]:10})")

# Mettre à jour quelques courses existantes en 'standard'
print("\n=== MISE À JOUR DES COURSES EXISTANTES ===")
cursor.execute("UPDATE courses SET categorie_demande = 'standard' WHERE categorie_demande IS NULL OR categorie_demande = ''")
updated = cursor.rowcount
print(f"✅ {updated} courses mises à jour avec categorie_demande='standard'")

# Vérifier quelques courses
print("\n=== EXEMPLE DE COURSES ===")
cursor.execute("""
    SELECT code_unique, categorie_demande, statut, date_demande 
    FROM courses 
    ORDER BY date_demande DESC 
    LIMIT 3
""")

for code, categorie, statut, date in cursor.fetchall():
    print(f"• {code}: {categorie} ({statut}) - {date}")

# Commit et fermer
conn.commit()
conn.close()

print("\n✅ CORRECTION TERMINÉE !")
print("================================================")