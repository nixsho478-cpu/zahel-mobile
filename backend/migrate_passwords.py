"""
Script de migration des mots de passe vers le nouveau format avec salt
"""
import sqlite3
import sys
import os
from auth_jwt import AuthService

def migrate_passwords():
    """Migrer tous les mots de passe vers le nouveau format"""
    
    # Chemin vers la base de données
    db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Migration des mots de passe...")
        
        # 1. Migrer les conducteurs
        cursor.execute("SELECT id, password_hash FROM conducteurs WHERE password_hash IS NOT NULL")
        conducteurs = cursor.fetchall()
        
        print(f"📊 {len(conducteurs)} conducteur(s) à migrer")
        
        for conducteur_id, old_hash in conducteurs:
            if old_hash and not old_hash.startswith('sha256$'):
                new_hash = AuthService.migrate_old_password(old_hash)
                cursor.execute(
                    "UPDATE conducteurs SET password_hash = ? WHERE id = ?",
                    (new_hash, conducteur_id)
                )
                print(f"  ✅ Conducteur {conducteur_id} migré")
        
        # 2. Migrer les clients
        cursor.execute("SELECT id, password_hash FROM clients WHERE password_hash IS NOT NULL")
        clients = cursor.fetchall()
        
        print(f"📊 {len(clients)} client(s) à migrer")
        
        for client_id, old_hash in clients:
            if old_hash and not old_hash.startswith('sha256$'):
                new_hash = AuthService.migrate_old_password(old_hash)
                cursor.execute(
                    "UPDATE clients SET password_hash = ? WHERE id = ?",
                    (new_hash, client_id)
                )
                print(f"  ✅ Client {client_id} migré")
        
        # 3. Migrer l'admin PDG
        cursor.execute("SELECT id, password_hash FROM admin_pdg WHERE password_hash IS NOT NULL")
        admins = cursor.fetchall()
        
        print(f"📊 {len(admins)} admin(s) à migrer")
        
        for admin_id, old_hash in admins:
            if old_hash and not old_hash.startswith('sha256$'):
                new_hash = AuthService.migrate_old_password(old_hash)
                cursor.execute(
                    "UPDATE admin_pdg SET password_hash = ? WHERE id = ?",
                    (new_hash, admin_id)
                )
                print(f"  ✅ Admin {admin_id} migré")
        
        conn.commit()
        conn.close()
        
        print("✅ Migration terminée avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_migration():
    """Tester la migration avec un exemple"""
    print("🧪 Test de migration...")
    
    # Ancien hash SHA-256 simple
    old_hash = hashlib.sha256("test123".encode()).hexdigest()
    print(f"Ancien hash: {old_hash}")
    
    # Nouveau hash avec salt
    new_hash = AuthService.migrate_old_password(old_hash)
    print(f"Nouveau hash: {new_hash}")
    
    # Vérifier que le nouveau hash est différent
    if old_hash != new_hash:
        print("✅ Le nouveau hash est différent (bon signe!)")
    
    # Vérifier le format
    if new_hash.startswith('sha256$'):
        print("✅ Format correct (sha256$salt$hash)")
    else:
        print("❌ Format incorrect")

if __name__ == '__main__':
    import hashlib
    
    print("=" * 60)
    print("🔐 MIGRATION DES MOTS DE PASSE ZAHEL")
    print("=" * 60)
    
    # Tester d'abord
    test_migration()
    
    print("\n" + "=" * 60)
    print("🚀 Lancer la migration complète?")
    print("Cette opération mettra à jour tous les mots de passe dans la base de données.")
    print("Assurez-vous d'avoir une sauvegarde avant de continuer.")
    
    response = input("\nContinuer? (oui/non): ").strip().lower()
    
    if response == 'oui':
        print("\n" + "=" * 60)
        success = migrate_passwords()
        
        if success:
            print("\n✅ Migration réussie!")
            print("⚠️  IMPORTANT: Les utilisateurs devront se reconnecter.")
            print("Le système utilisera désormais JWT pour l'authentification.")
        else:
            print("\n❌ Échec de la migration")
    else:
        print("\n❌ Migration annulée")
    
    print("=" * 60)