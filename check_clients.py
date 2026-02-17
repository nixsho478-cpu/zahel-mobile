# check_clients.py
import sqlite3

print("📋 LISTE DES CLIENTS EXISTANTS")
print("=" * 50)

# Chemin vers votre base de données
db_path = "database/zahel_secure.db"

try:
    # Se connecter à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"✅ Connexion à la base: {db_path}")
    
    # 1. Vérifier si la table 'clients' existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("❌ La table 'clients' n'existe pas!")
    else:
        print("✅ Table 'clients' existe")
        
        # 2. Voir les colonnes
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        
        print(f"\n📊 Structure de la table ({len(columns)} colonnes):")
        for col in columns:
            print(f"  {col[0]}. {col[1]} ({col[2]})")
        
        # 3. Compter les clients
        cursor.execute("SELECT COUNT(*) FROM clients")
        count = cursor.fetchone()[0]
        print(f"\n👥 Nombre total de clients: {count}")
        
        # 4. Lister tous les clients
        if count > 0:
            cursor.execute("SELECT id, telephone, nom, compte_suspendu FROM clients ORDER BY id")
            clients = cursor.fetchall()
            
            print("\n📋 Liste des clients:")
            for client in clients:
                status = "✅ Actif" if client[3] == 0 else "❌ Suspendu"
                print(f"  ID {client[0]}: {client[2]} - {client[1]} - {status}")
        else:
            print("⚠️ Aucun client dans la base de données")
    
    # 5. Vérifier aussi la table conducteurs
    print("\n" + "=" * 50)
    cursor.execute("SELECT COUNT(*) FROM conducteurs")
    count_conducteurs = cursor.fetchone()[0]
    print(f"🚗 Nombre de conducteurs: {count_conducteurs}")
    
    if count_conducteurs > 0:
        cursor.execute("SELECT id, immatricule, nom, telephone FROM conducteurs LIMIT 5")
        conducteurs = cursor.fetchall()
        print("📋 Conducteurs (premiers 5):")
        for cond in conducteurs:
            print(f"  {cond[1]}: {cond[2]} - {cond[3]}")
    
    conn.close()
    print("\n✅ Vérification terminée!")
    
except sqlite3.Error as e:
    print(f"❌ Erreur SQLite: {e}")
except Exception as e:
    print(f"❌ Erreur générale: {e}")