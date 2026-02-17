# create_amendes_correct.py
import sqlite3
import os

print("=" * 60)
print("CRÉATION DE LA TABLE AMENDES POUR ZAHEL - VERSION CORRIGÉE")
print("=" * 60)

# Chemin VERS LA BONNE BASE
db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"

print(f"📁 Base cible : {db_path}")
print(f"📊 Taille : {os.path.getsize(db_path) / 1024:.1f} KB")

# Connexion à la base
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # Pour avoir les noms de colonnes
cursor = conn.cursor()

print("\n📋 TABLES EXISTANTES (14 attendues) :")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print(f"✅ {len(tables)} tables trouvées :")
for table in tables:
    print(f"  • {table['name']}")

# Vérifier spécifiquement la table clients
print("\n🔍 VÉRIFICATION TABLE 'clients' :")
cursor.execute("PRAGMA table_info(clients)")
columns = cursor.fetchall()
if columns:
    print(f"✅ Table 'clients' existe avec {len(columns)} colonnes :")
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")
    
    # Vérifier qu'il y a des clients
    cursor.execute("SELECT COUNT(*) as count FROM clients")
    count = cursor.fetchone()['count']
    print(f"  👥 {count} client(s) dans la base")
else:
    print("❌ Table 'clients' non trouvée !")
    conn.close()
    exit(1)

# Vérifier si la table amendes existe déjà
print("\n🔍 VÉRIFICATION TABLE 'amendes' :")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='amendes'")
if cursor.fetchone():
    print("⚠️ Table 'amendes' existe déjà !")
    # Afficher sa structure
    cursor.execute("PRAGMA table_info(amendes)")
    existing_columns = cursor.fetchall()
    print("  Structure actuelle :")
    for col in existing_columns:
        print(f"  - {col['name']} ({col['type']})")
    
    response = input("\n❓ Veux-tu la recréer ? (o/n) : ")
    if response.lower() != 'o':
        print("Annulation.")
        conn.close()
        exit(0)
    else:
        # Supprimer l'ancienne table
        cursor.execute("DROP TABLE IF EXISTS amendes")
        print("✅ Ancienne table supprimée")
else:
    print("✅ Table 'amendes' n'existe pas encore")

# Créer la table amendes
print("\n🛠️ CRÉATION DE LA TABLE 'amendes'...")
create_table_sql = """
CREATE TABLE amendes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    montant INTEGER NOT NULL,
    raison TEXT NOT NULL,
    statut TEXT DEFAULT 'impayee',
    course_concerne TEXT,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_paiement DATETIME,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);
"""

try:
    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ Table 'amendes' créée avec succès !")
    
    # Vérifier la création
    cursor.execute("PRAGMA table_info(amendes)")
    new_columns = cursor.fetchall()
    print(f"\n📋 STRUCTURE DE 'amendes' ({len(new_columns)} colonnes) :")
    for col in new_columns:
        nullable = "NOT NULL" if not col['notnull'] else ""
        print(f"  • {col['name']:20} {col['type']:15} {nullable}")
    
    # Ajouter un index pour les performances
    cursor.execute("CREATE INDEX idx_amendes_client_statut ON amendes(client_id, statut)")
    conn.commit()
    print("✅ Index créé pour accélérer les recherches")
    
except Exception as e:
    print(f"❌ ERREUR lors de la création : {e}")
    import traceback
    traceback.print_exc()

# Test : insérer une amende de test
print("\n🧪 TEST : Création d'une amende de test...")
try:
    # Récupérer un client existant
    cursor.execute("SELECT id, telephone FROM clients LIMIT 1")
    client = cursor.fetchone()
    
    if client:
        test_sql = """
        INSERT INTO amendes (client_id, montant, raison, course_concerne)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(test_sql, (client['id'], 500, 'annulation_tardive', 'ZAHEL-TEST001'))
        conn.commit()
        print(f"✅ Amende de test créée pour le client {client['telephone']}")
        print(f"   Montant : 500 KMF")
        print(f"   Raison : annulation_tardive")
    else:
        print("⚠️ Aucun client trouvé pour le test")
        
except Exception as e:
    print(f"⚠️ Test non exécuté : {e}")

# Fermer la connexion
conn.close()

print("\n" + "=" * 60)
print("✅ SCRIPT TERMINÉ AVEC SUCCÈS !")
print("=" * 60)
input("\nAppuie sur ENTRÉE pour quitter...")