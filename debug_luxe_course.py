# debug_luxe_course_corrected.py
import sqlite3
import requests
import json

DB_PATH = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"
API_BASE = "http://localhost:5001"

def debug_luxe_course():
    # 1. Vérifier la base de données
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=== DERNIÈRES 5 COURSES ===")
    cursor.execute("""
        SELECT code_unique, categorie_demande, prix_convenu, statut, date_creation
        FROM courses 
        ORDER BY date_creation DESC 
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"Code: {row[0]}")
        print(f"Catégorie: {row[1]}")
        print(f"Prix: {row[2]} KMF")
        print(f"Statut: {row[3]}")
        print(f"Date: {row[4]}")
        print("-" * 40)
    
    conn.close()

if __name__ == "__main__":
    debug_luxe_course()