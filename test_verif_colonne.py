# test_verif_colonne.py
import sqlite3

conn = sqlite3.connect(r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db")
cursor = conn.cursor()

# Vérifier la structure
cursor.execute("PRAGMA table_info(courses)")
columns = cursor.fetchall()
print("=== COLONNES DE LA TABLE COURSES ===")
for col in columns:
    print(f"{col[1]} ({col[2]}) - {'NULL' if col[3] else 'NOT NULL'}")

conn.close()