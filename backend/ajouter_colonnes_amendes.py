# ajouter_colonnes_amendes.py
import sqlite3
import os

print("=" * 60)
print("AJOUT DE COLONNES AMENDE À LA TABLE 'courses'")
print("=" * 60)

db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"

if not os.path.exists(db_path):
    print(f"❌ Base de données non trouvée : {db_path}")
    exit(1)

print(f"📁 Base de données : {db_path}")
print(f"📊 Taille : {os.path.getsize(db_path) / 1024:.1f} KB")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Vérifier la structure actuelle de la table 'courses'
print("\n🔍 STRUCTURE ACTUELLE DE 'courses' :")
cursor.execute("PRAGMA table_info(courses)")
colonnes = cursor.fetchall()
print(f"✅ {len(colonnes)} colonnes trouvées :")
for col in colonnes:
    print(f"  • {col[1]} ({col[2]})")

# 2. Vérifier si les colonnes existent déjà
colonnes_existantes = [col[1] for col in colonnes]
colonnes_a_ajouter = []

if 'amende_incluse' not in colonnes_existantes:
    colonnes_a_ajouter.append('amende_incluse TEXT')
if 'montant_amende' not in colonnes_existantes:
    colonnes_a_ajouter.append('montant_amende DECIMAL(10,2) DEFAULT 0')
if 'amendes_ids' not in colonnes_existantes:
    colonnes_a_ajouter.append('amendes_ids TEXT')

if not colonnes_a_ajouter:
    print("\n✅ Toutes les colonnes amendes existent déjà !")
else:
    print(f"\n🛠️  Colonnes à ajouter ({len(colonnes_a_ajouter)}) :")
    for col in colonnes_a_ajouter:
        print(f"  • {col}")

    # 3. Ajouter les colonnes
    print("\n⚙️  Ajout des colonnes...")
    try:
        for col in colonnes_a_ajouter:
            col_nom = col.split()[0]
            sql = f"ALTER TABLE courses ADD COLUMN {col}"
            print(f"  Exécution : {sql}")
            cursor.execute(sql)
        
        conn.commit()
        print("✅ Colonnes ajoutées avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout : {e}")
        print("Essai d'une autre méthode...")
        
        # Méthode alternative : recréer la table
        try:
            print("\n🔄 Méthode alternative : modification structure...")
            
            # Pour SQLite, on doit recréer la table
            # 1. Créer une table temporaire
            cursor.execute('''
            CREATE TABLE courses_temp AS SELECT * FROM courses
            ''')
            
            # 2. Supprimer l'ancienne table
            cursor.execute('DROP TABLE courses')
            
            # 3. Recréer la table avec les nouvelles colonnes
            cursor.execute('''
            CREATE TABLE courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_unique TEXT NOT NULL UNIQUE,
                client_id INTEGER NOT NULL,
                conducteur_id INTEGER,
                conducteur_demande_specifique TEXT,
                prix_convenu DECIMAL(10,2) NOT NULL,
                point_depart_lat DECIMAL(9,6),
                point_depart_lng DECIMAL(9,6),
                point_arrivee_lat DECIMAL(9,6),
                point_arrivee_lng DECIMAL(9,6),
                statut TEXT DEFAULT 'en_attente',
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_debut TIMESTAMP,
                date_fin TIMESTAMP,
                prix_final DECIMAL(10,2),
                paiement_effectue BOOLEAN DEFAULT 0,
                amende_incluse TEXT,
                montant_amende DECIMAL(10,2) DEFAULT 0,
                amendes_ids TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(id),
                FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id)
            )
            ''')
            
            # 4. Copier les données
            cursor.execute('''
            INSERT INTO courses (
                id, code_unique, client_id, conducteur_id, 
                conducteur_demande_specifique, prix_convenu,
                point_depart_lat, point_depart_lng,
                point_arrivee_lat, point_arrivee_lng,
                statut, date_creation, date_debut, date_fin,
                prix_final, paiement_effectue
            )
            SELECT 
                id, code_unique, client_id, conducteur_id, 
                conducteur_demande_specifique, prix_convenu,
                point_depart_lat, point_depart_lng,
                point_arrivee_lat, point_arrivee_lng,
                statut, date_creation, date_debut, date_fin,
                prix_final, paiement_effectue
            FROM courses_temp
            ''')
            
            # 5. Supprimer la table temporaire
            cursor.execute('DROP TABLE courses_temp')
            
            conn.commit()
            print("✅ Table 'courses' recréée avec les nouvelles colonnes !")
            
        except Exception as e2:
            print(f"❌ Erreur méthode alternative : {e2}")
            conn.rollback()

# 4. Vérifier la nouvelle structure
print("\n🔍 NOUVELLE STRUCTURE DE 'courses' :")
cursor.execute("PRAGMA table_info(courses)")
nouvelles_colonnes = cursor.fetchall()
print(f"📊 {len(nouvelles_colonnes)} colonnes :")
for col in nouvelles_colonnes:
    print(f"  • {col[1]:25} {col[2]:15}")

# 5. Vérifier s'il y a des données
cursor.execute("SELECT COUNT(*) as count FROM courses")
count = cursor.fetchone()[0]
print(f"\n📊 {count} courses dans la table")

conn.close()

print("\n" + "=" * 60)
print("SCRIPT TERMINÉ")
print("=" * 60)
input("\nAppuie sur ENTRÉE pour quitter...")