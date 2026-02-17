# ajouter_colonne_timer.py
import sqlite3

print("⏱️ AJOUT COLONNE TIMER LUXE")
print("=" * 50)

db_path = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Ajouter date_debut_recherche_luxe si elle n'existe pas
    cursor.execute("PRAGMA table_info(courses)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'date_debut_recherche_luxe' not in columns:
        cursor.execute("ALTER TABLE courses ADD COLUMN date_debut_recherche_luxe TEXT")
        print("✅ Colonne 'date_debut_recherche_luxe' ajoutée")
    else:
        print("✅ Colonne existe déjà")
    
    # 2. Vérifier
    cursor.execute("PRAGMA table_info(courses)")
    print("\n📋 COLONNES COURSES (extrait):")
    for row in cursor.fetchall():
        if 'luxe' in row[1] or 'categorie' in row[1] or 'date' in row[1]:
            print(f"  • {row[1]} ({row[2]})")
    
    conn.commit()
    conn.close()
    print("\n✅ Base de données prête !")
    
except Exception as e:
    print(f"❌ ERREUR: {e}")