# ajouter_colonne_taxes.py
import sqlite3
import os

print("=" * 60)
print("🔧 MISE À JOUR DE LA BASE DE DONNÉES ZAHEL")
print("=" * 60)

# Chemin vers la base de données
db_path = "database/zahel_secure.db"

if not os.path.exists(db_path):
    print(f"❌ Base de données non trouvée: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📊 Vérification des colonnes existantes...")
    
    # Vérifier si la colonne taxes_zahel existe déjà
    cursor.execute("PRAGMA table_info(courses)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print("Colonnes actuelles de la table 'courses':")
    for col in columns:
        print(f"  • {col[1]} ({col[2]})")
    
    if 'taxes_zahel' not in column_names:
        print("\n➕ Ajout de la colonne 'taxes_zahel'...")
        cursor.execute("ALTER TABLE courses ADD COLUMN taxes_zahel DECIMAL DEFAULT 0")
        conn.commit()
        print("✅ Colonne 'taxes_zahel' ajoutée avec succès !")
        
        # Mettre à jour les courses existantes avec les taxes calculées
        print("\n📝 Mise à jour des courses existantes...")
        cursor.execute('''
            UPDATE courses 
            SET taxes_zahel = prix_convenu * 0.05 
            WHERE statut = 'terminee' AND taxes_zahel IS NULL
        ''')
        updated = cursor.rowcount
        conn.commit()
        print(f"✅ {updated} courses mises à jour avec les taxes (5%)")
    else:
        print("\n✅ La colonne 'taxes_zahel' existe déjà !")
    
    # Vérifier aussi la colonne prix_final
    if 'prix_final' not in column_names:
        print("\n➕ Ajout de la colonne 'prix_final'...")
        cursor.execute("ALTER TABLE courses ADD COLUMN prix_final DECIMAL DEFAULT 0")
        conn.commit()
        print("✅ Colonne 'prix_final' ajoutée avec succès !")
        
        # Copier prix_convenu dans prix_final pour les courses terminées
        cursor.execute('''
            UPDATE courses 
            SET prix_final = prix_convenu 
            WHERE statut = 'terminee' AND prix_final IS NULL
        ''')
        conn.commit()
    else:
        print("✅ La colonne 'prix_final' existe déjà !")
    
    conn.close()
    print("\n🎉 Mise à jour de la base de données terminée !")
    
except Exception as e:
    print(f"\n💥 Erreur: {e}")

print("\n" + "=" * 60)
input("Appuie sur ENTREE pour redémarrer le serveur...")