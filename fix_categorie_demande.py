# fix_categorie_demande.py
import sqlite3
import os

print("🔧 CORRECTION COLONNE CATEGORIE_DEMANDE")
print("========================================")

# Chemin de la base de données
db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"
backup_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure_backup.db"

# 1. Créer une sauvegarde
print("1. Création de sauvegarde...")
if os.path.exists(db_path):
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"   ✅ Sauvegarde créée: {backup_path}")

# 2. Se connecter à la base
print("2. Connexion à la base de données...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 3. Vérifier si la colonne existe déjà
print("3. Vérification structure de la table 'courses'...")
cursor.execute("PRAGMA table_info(courses)")
columns = [col[1] for col in cursor.fetchall()]
print(f"   Colonnes existantes: {', '.join(columns)}")

if 'categorie_demande' in columns:
    print("   ✅ Colonne 'categorie_demande' existe déjà")
else:
    print("   ❌ Colonne 'categorie_demande' manquante - Ajout en cours...")
    
    # 4. Ajouter la colonne
    try:
        cursor.execute("ALTER TABLE courses ADD COLUMN categorie_demande TEXT DEFAULT 'standard'")
        print("   ✅ Colonne ajoutée avec succès")
        
        # 5. Mettre à jour les courses existantes
        print("5. Mise à jour des courses existantes...")
        
        # Compter les courses
        cursor.execute("SELECT COUNT(*) FROM courses")
        total = cursor.fetchone()[0]
        print(f"   Total courses: {total}")
        
        # Mettre à jour toutes les courses en 'standard' par défaut
        cursor.execute("UPDATE courses SET categorie_demande = 'standard' WHERE categorie_demande IS NULL")
        updated = cursor.rowcount
        print(f"   Courses mises à jour: {updated}")
        
        # 6. Vérifier quelques courses
        print("\n6. Vérification de quelques courses...")
        cursor.execute("""
            SELECT code_unique, categorie_demande, statut 
            FROM courses 
            ORDER BY date_creation DESC 
            LIMIT 5
        """)
        
        courses = cursor.fetchall()
        for code, categorie, statut in courses:
            print(f"   • {code}: {categorie} ({statut})")
            
    except Exception as e:
        print(f"   ❌ Erreur lors de l'ajout: {e}")
        conn.rollback()
        raise

# 7. Vérifier aussi la colonne timer_luxe_demarre_le
print("\n7. Vérification colonne 'timer_luxe_demarre_le'...")
if 'timer_luxe_demarre_le' in columns:
    print("   ✅ Colonne 'timer_luxe_demarre_le' existe déjà")
else:
    print("   ❌ Colonne 'timer_luxe_demarre_le' manquante - Ajout...")
    try:
        cursor.execute("ALTER TABLE courses ADD COLUMN timer_luxe_demarre_le TIMESTAMP")
        print("   ✅ Colonne ajoutée")
    except Exception as e:
        print(f"   ⚠️ Erreur: {e}")

# 8. Commit et fermeture
conn.commit()
conn.close()

print("\n✅ CORRECTION TERMINÉE !")
print("========================================")
print("Redémarre ton API et teste à nouveau.")