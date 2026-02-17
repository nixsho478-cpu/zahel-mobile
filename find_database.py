# find_database.py
import os
import sys

print("🔍 RECHERCHE DE LA BASE DE DONNÉES ZAHEL")
print("=" * 50)

# Chercher depuis le dossier Desktop/zahel
start_path = r"C:\Users\USER\Desktop\zahel"

db_files = []
for root, dirs, files in os.walk(start_path):
    for file in files:
        if "zahel" in file.lower() and file.endswith(".db"):
            full_path = os.path.join(root, file)
            size_kb = os.path.getsize(full_path) / 1024
            db_files.append((full_path, size_kb))

if db_files:
    print(f"✅ {len(db_files)} base(s) de données trouvée(s) :")
    for i, (path, size) in enumerate(db_files, 1):
        print(f"\n{i}. {path}")
        print(f"   Taille : {size:.1f} KB")
        
        # Afficher les tables
        import sqlite3
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"   Tables : {len(tables)}")
            conn.close()
        except:
            print("   ⚠️ Impossible d'ouvrir")
else:
    print("❌ Aucune base de données trouvée")

print("\n" + "=" * 50)
input("Appuie sur ENTRÉE pour quitter...")