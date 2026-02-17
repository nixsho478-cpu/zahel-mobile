# ajouter_config_luxe.py
import sqlite3
import os

print("⚙️ AJOUT CONFIGURATION RECHERCHE LUXE")
print("=" * 50)

db_path = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"

if not os.path.exists(db_path):
    print(f"❌ Base non trouvée: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Vérifier si la configuration existe déjà
    cursor.execute("SELECT cle FROM configuration WHERE cle LIKE '%luxe%'")
    existing = cursor.fetchall()
    
    if existing:
        print("✅ Configuration luxe existe déjà:")
        for row in existing:
            print(f"  • {row[0]}")
    else:
        # Ajouter les configurations
        configs = [
            ('temps_recherche_luxe', '300', 'Temps max recherche luxe (secondes)', 1),
            ('message_attente_luxe', 'Recherche véhicule luxe en cours... Peut prendre quelques minutes.', 'Message attente luxe', 1),
            ('message_timeout_luxe', '⏱️ Aucun véhicule luxe disponible après 5 minutes. Voulez-vous continuer en Confort ?', 'Message timeout luxe', 1)
        ]
        
        cursor.executemany('''
            INSERT INTO configuration (cle, valeur, description, modifiable)
            VALUES (?, ?, ?, ?)
        ''', configs)
        
        conn.commit()
        print("✅ Configuration luxe ajoutée avec succès !")
    
    # Afficher la configuration
    print("\n📋 CONFIGURATION ACTUELLE LUXE:")
    cursor.execute("SELECT cle, valeur, description FROM configuration WHERE cle LIKE '%luxe%'")
    for row in cursor.fetchall():
        print(f"  • {row[0]}: {row[1]}")
        print(f"    {row[2]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()