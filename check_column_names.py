# check_column_names.py
import sqlite3

DB_PATH = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"

def check_columns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lister toutes les colonnes de la table courses
    cursor.execute("PRAGMA table_info(courses)")
    
    print("=== COLONNES DE LA TABLE COURSES ===")
    for col in cursor.fetchall():
        print(f"{col[0]}: {col[1]} (type: {col[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_columns()