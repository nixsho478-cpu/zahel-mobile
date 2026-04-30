"""
Script pour corriger les incohérences de colonnes dans l'API ZAHEL
"""
import sqlite3
import os
from datetime import datetime

def fix_column_inconsistencies():
    """Corriger toutes les incohérences de colonnes dans la base de données"""
    
    # Chemin vers la base de données
    db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Correction des incohérences de colonnes...")
        print("=" * 60)
        
        # ===== 1. TABLE COURSES =====
        print("\n📋 TABLE COURSES")
        print("-" * 40)
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(courses)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes actuelles: {columns}")
        
        # Colonnes à ajouter si manquantes
        missing_columns = []
        
        # Colonnes standardisées
        required_columns = [
            ('depart_lat', 'REAL'),
            ('depart_lng', 'REAL'),
            ('arrivee_lat', 'REAL'),
            ('arrivee_lng', 'REAL'),
            ('distance_km', 'REAL'),
            ('taxes_zahel', 'DECIMAL(10,2)'),
            ('categorie_demande', 'TEXT DEFAULT "standard"'),
            ('adresse_depart', 'TEXT'),
            ('adresse_arrivee', 'TEXT'),
            ('date_debut_recherche_luxe', 'DATETIME'),
            ('amende_incluse', 'BOOLEAN DEFAULT 0'),
            ('montant_amende', 'DECIMAL(10,2) DEFAULT 0'),
            ('amendes_ids', 'TEXT')
        ]
        
        for col_name, col_type in required_columns:
            if col_name not in columns:
                missing_columns.append((col_name, col_type))
                print(f"  ❌ Manquante: {col_name} ({col_type})")
        
        # Ajouter les colonnes manquantes
        for col_name, col_type in missing_columns:
            try:
                cursor.execute(f'ALTER TABLE courses ADD COLUMN {col_name} {col_type}')
                print(f"  ✅ Ajoutée: {col_name}")
            except Exception as e:
                print(f"  ⚠️  Erreur ajout {col_name}: {e}")
        
        # ===== 2. TABLE CONDUCTEURS =====
        print("\n📋 TABLE CONDUCTEURS")
        print("-" * 40)
        
        cursor.execute("PRAGMA table_info(conducteurs)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes actuelles: {columns}")
        
        # Colonnes à ajouter
        required_columns_conducteurs = [
            ('taxes_cumulees', 'DECIMAL(10,2) DEFAULT 0'),
            ('interruptions_jour', 'INTEGER DEFAULT 0'),
            ('date_derniere_interruption', 'DATE'),
            ('note_moyenne', 'DECIMAL(3,2) DEFAULT 5.0'),
            ('last_position_update', 'DATETIME')
        ]
        
        for col_name, col_type in required_columns_conducteurs:
            if col_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE conducteurs ADD COLUMN {col_name} {col_type}')
                    print(f"  ✅ Ajoutée: {col_name}")
                except Exception as e:
                    print(f"  ⚠️  Erreur ajout {col_name}: {e}")
        
        # ===== 3. TABLE CLIENTS =====
        print("\n📋 TABLE CLIENTS")
        print("-" * 40)
        
        cursor.execute("PRAGMA table_info(clients)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes actuelles: {columns}")
        
        # Colonnes à ajouter
        required_columns_clients = [
            ('courses_effectuees', 'INTEGER DEFAULT 0'),
            ('depenses_totales', 'DECIMAL(10,2) DEFAULT 0'),
            ('date_suspension', 'DATETIME'),
            ('motif_suspension', 'TEXT')
        ]
        
        for col_name, col_type in required_columns_clients:
            if col_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE clients ADD COLUMN {col_name} {col_type}')
                    print(f"  ✅ Ajoutée: {col_name}")
                except Exception as e:
                    print(f"  ⚠️  Erreur ajout {col_name}: {e}")
        
        # ===== 4. TABLE ADMIN_PDG =====
        print("\n📋 TABLE ADMIN_PDG")
        print("-" * 40)
        
        cursor.execute("PRAGMA table_info(admin_pdg)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes actuelles: {columns}")
        
        # Colonnes à ajouter
        required_columns_admin = [
            ('permissions', 'TEXT DEFAULT "admin"'),
            ('last_login', 'DATETIME')
        ]
        
        for col_name, col_type in required_columns_admin:
            if col_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE admin_pdg ADD COLUMN {col_name} {col_type}')
                    print(f"  ✅ Ajoutée: {col_name}")
                except Exception as e:
                    print(f"  ⚠️  Erreur ajout {col_name}: {e}")
        
        # ===== 5. TABLE STATISTIQUES =====
        print("\n📋 TABLE STATISTIQUES")
        print("-" * 40)
        
        cursor.execute("PRAGMA table_info(statistiques)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes actuelles: {columns}")
        
        # Colonnes à ajouter
        required_columns_stats = [
            ('courses_annulees', 'INTEGER DEFAULT 0'),
            ('courses_en_cours', 'INTEGER DEFAULT 0'),
            ('conducteurs_en_ligne', 'INTEGER DEFAULT 0'),
            ('clients_actifs', 'INTEGER DEFAULT 0')
        ]
        
        for col_name, col_type in required_columns_stats:
            if col_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE statistiques ADD COLUMN {col_name} {col_type}')
                    print(f"  ✅ Ajoutée: {col_name}")
                except Exception as e:
                    print(f"  ⚠️  Erreur ajout {col_name}: {e}")
        
        # ===== 6. MIGRATION DES DONNÉES EXISTANTES =====
        print("\n🔄 MIGRATION DES DONNÉES")
        print("-" * 40)
        
        # Migrer les colonnes de position si elles existent sous d'autres noms
        try:
            # Vérifier si point_depart_lat existe mais pas depart_lat
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses'")
            if cursor.fetchone():
                # Copier les données des anciennes colonnes vers les nouvelles
                migration_queries = [
                    # Courses: point_depart_lat → depart_lat
                    "UPDATE courses SET depart_lat = point_depart_lat WHERE point_depart_lat IS NOT NULL AND depart_lat IS NULL",
                    "UPDATE courses SET depart_lng = point_depart_lng WHERE point_depart_lng IS NOT NULL AND depart_lng IS NULL",
                    "UPDATE courses SET arrivee_lat = point_arrivee_lat WHERE point_arrivee_lat IS NOT NULL AND arrivee_lat IS NULL",
                    "UPDATE courses SET arrivee_lng = point_arrivee_lng WHERE point_arrivee_lng IS NOT NULL AND arrivee_lng IS NULL"
                ]
                
                for query in migration_queries:
                    try:
                        cursor.execute(query)
                        rows = cursor.rowcount
                        if rows > 0:
                            print(f"  ✅ Migration: {rows} ligne(s) mise(s) à jour")
                    except Exception as e:
                        print(f"  ⚠️  Erreur migration: {e}")
        except Exception as e:
            print(f"  ⚠️  Erreur lors de la migration: {e}")
        
        # ===== 7. CRÉER LES TABLES MANQUANTES =====
        print("\n🏗️  CRÉATION DES TABLES MANQUANTES")
        print("-" * 40)
        
        # Table notifications_conducteur
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications_conducteur'")
        if not cursor.fetchone():
            try:
                cursor.execute('''
                    CREATE TABLE notifications_conducteur (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conducteur_id INTEGER NOT NULL,
                        course_code TEXT,
                        type_notification TEXT NOT NULL,
                        message TEXT NOT NULL,
                        lue BOOLEAN DEFAULT 0,
                        date_lecture DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id) ON DELETE CASCADE
                    )
                ''')
                print("  ✅ Table 'notifications_conducteur' créée")
            except Exception as e:
                print(f"  ⚠️  Erreur création table: {e}")
        
        # Table adresses_frequentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='adresses_frequentes'")
        if not cursor.fetchone():
            try:
                cursor.execute('''
                    CREATE TABLE adresses_frequentes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id INTEGER NOT NULL,
                        nom TEXT NOT NULL,
                        adresse TEXT NOT NULL,
                        latitude REAL,
                        longitude REAL,
                        type TEXT DEFAULT 'personnel',
                        est_principale BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                    )
                ''')
                print("  ✅ Table 'adresses_frequentes' créée")
            except Exception as e:
                print(f"  ⚠️  Erreur création table: {e}")
        
        # Table historique_conducteur
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historique_conducteur'")
        if not cursor.fetchone():
            try:
                cursor.execute('''
                    CREATE TABLE historique_conducteur (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conducteur_id INTEGER NOT NULL,
                        mois TEXT NOT NULL,
                        courses_effectuees INTEGER DEFAULT 0,
                        gains_totaux DECIMAL(10,2) DEFAULT 0,
                        taxes_payees DECIMAL(10,2) DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id) ON DELETE CASCADE
                    )
                ''')
                print("  ✅ Table 'historique_conducteur' créée")
            except Exception as e:
                print(f"  ⚠️  Erreur création table: {e}")
        
        # ===== 8. CRÉER LES INDEX =====
        print("\n📊 CRÉATION DES INDEX")
        print("-" * 40)
        
        indexes = [
            ("idx_courses_statut", "courses(statut)"),
            ("idx_courses_client", "courses(client_id)"),
            ("idx_courses_conducteur", "courses(conducteur_id)"),
            ("idx_conducteurs_disponible", "conducteurs(disponible, en_course)"),
            ("idx_conducteurs_categorie", "conducteurs(categorie_vehicule)"),
            ("idx_clients_telephone", "clients(telephone)"),
            ("idx_notifications_conducteur", "notifications_conducteur(conducteur_id, lue)"),
            ("idx_adresses_client", "adresses_frequentes(client_id)")
        ]
        
        for idx_name, idx_def in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def}")
                print(f"  ✅ Index '{idx_name}' créé")
            except Exception as e:
                print(f"  ⚠️  Erreur création index {idx_name}: {e}")
        
        # ===== 9. VALIDATION =====
        print("\n✅ VALIDATION")
        print("-" * 40)
        
        # Compter les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"📊 {len(tables)} tables dans la base de données:")
        for table in tables:
            print(f"  • {table[0]}")
        
        # Vérifier les colonnes critiques
        critical_tables = ['courses', 'conducteurs', 'clients', 'admin_pdg']
        for table in critical_tables:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [col[1] for col in cursor.fetchall()]
            print(f"\n📋 {table} ({len(cols)} colonnes):")
            print(f"  {', '.join(cols[:10])}...")
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 CORRECTIONS TERMINÉES AVEC SUCCÈS!")
        print("=" * 60)
        print("\n📋 RÉSUMÉ:")
        print("• Colonnes standardisées dans toutes les tables")
        print("• Tables manquantes créées")
        print("• Index optimisés pour les performances")
        print("• Migration des données existantes")
        print("\n⚠️  IMPORTANT:")
        print("• Redémarrer le serveur API pour appliquer les changements")
        print("• Tester les endpoints critiques")
        print("• Vérifier la compatibilité avec les applications mobiles")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fixes():
    """Tester les corrections appliquées"""
    print("\n🧪 TEST DES CORRECTIONS")
    print("=" * 60)
    
    db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Vérifier les tables essentielles
        essential_tables = ['courses', 'conducteurs', 'clients', 'admin_pdg', 'notifications_conducteur', 'adresses_frequentes']
        
        for table in essential_tables:
            cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone()[0] > 0
            status = "✅" if exists else "❌"
            print(f"{status} Table '{table}': {'PRÉSENTE' if exists else 'ABSENTE'}")
        
        # Test 2: Vérifier les colonnes critiques
        critical_columns = {
            'courses': ['depart_lat', 'depart_lng', 'arrivee_lat', 'arrivee_lng', 'categorie_demande'],
            'conducteurs': ['taxes_cumulees', 'note_moyenne'],
            'clients': ['courses_effectuees', 'depenses_totales']
        }
        
        for table, columns in critical_columns.items():
            cursor.execute(f"PRAGMA table_info({table})")
            existing_cols = [col[1] for col in cursor.fetchall()]
            
            print(f"\n📋 {table}:")
            for col in columns:
                exists = col in existing_cols
                status = "✅" if exists else "❌"
                print(f"  {status} {col}: {'PRÉSENTE' if exists else 'ABSENTE'}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("🧪 TESTS TERMINÉS")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 CORRECTION DES INCOHÉRENCES DE COLONNES ZAHEL")
    print("=" * 60)
    
    print("\n⚠️  AVERTISSEMENT:")
    print("Cette opération va modifier la structure de la base de données.")
    print("Assurez-vous d'avoir une sauvegarde avant de continuer.")
    
    response = input("\nContinuer? (oui/non): ").strip().lower()
    
    if response == 'oui':
        print("\n" + "=" * 60)
        
        # Appliquer les corrections
        success = fix_column_inconsistencies()
        
        if success:
            # Tester les corrections
            test_fixes()
            
            print("\n" + "=" * 60)
            print("🎉 OPÉRATION RÉUSSIE!")
            print("=" * 60)
            print("\n📋 PROCHAINES ÉTAPES:")
            print("1. Redémarrer le serveur API")
            print("2. Tester les endpoints critiques")
            print("3. Vérifier la compatibilité avec les applications mobiles")
            print("4. Exécuter les tests automatisés")
            print("5. Documenter les changements dans le CHANGELOG.md")
            
        else:
            print("\n❌ OPÉRATION ÉCHOUÉE!")
            print("Veuillez vérifier les erreurs ci-dessus.")
    
    else:
        print("\n❌ Opération annulée par l'utilisateur.")
        print("Aucune modification n'a été apportée à la base de données.")
