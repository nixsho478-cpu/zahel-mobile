# ajouter_colonne.py
import sqlite3
import os

print("🔧 AJOUT DE LA COLONNE CATÉGORIE_DEMANDE")
print("=" * 50)

# Chemin de la base
db_path = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"

if not os.path.exists(db_path):
    print(f"❌ Base de données non trouvée: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Vérifier si la colonne existe déjà
    cursor.execute("PRAGMA table_info(courses)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'categorie_demande' in columns:
        print("✅ La colonne 'categorie_demande' existe déjà")
    else:
        # 2. Ajouter la colonne
        cursor.execute("ALTER TABLE courses ADD COLUMN categorie_demande TEXT DEFAULT 'standard'")
        print("✅ Colonne 'categorie_demande' ajoutée")
        
        # 3. Mettre à jour les courses existantes
        cursor.execute("UPDATE courses SET categorie_demande = 'standard'")
        print("✅ Courses existantes mises à jour avec categorie='standard'")
        
        conn.commit()
        print("✅ Commit effectué")
    
    # 4. Vérification
    print("\n📋 VÉRIFICATION FINALE")
    print("-" * 30)
    
    cursor.execute("PRAGMA table_info(courses)")
    print("Colonnes de la table 'courses':")
    for row in cursor.fetchall():
        if row[1] in ['code_unique', 'statut', 'categorie_demande', 'prix_convenu']:
            print(f"  • {row[1]} ({row[2]})")
    
    # Compter les courses
    cursor.execute("SELECT COUNT(*) FROM courses")
    total = cursor.fetchone()[0]
    print(f"\nTotal courses: {total}")
    
    conn.close()
    print("\n✅ Opération terminée avec succès !")
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()