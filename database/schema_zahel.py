# schema_zahel.py - Structure complète de la base ZAHEL
import sqlite3
import os

class DatabaseZahel:
    def __init__(self, db_path='zahel_secure.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Créer une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialiser toutes les tables de la base"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print("🔨 Création de la structure ZAHEL...")
        
        # === TABLE : ADMIN PDG ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_pdg (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            secret_key TEXT UNIQUE,
            last_login DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # === TABLE : CONDUCTEURS ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conducteurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            immatricule TEXT UNIQUE NOT NULL,
            nom TEXT NOT NULL,
            telephone TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            nationalite TEXT,
            numero_identite TEXT UNIQUE,
            photo_identite_path TEXT,
            photo_visage_path TEXT,
            categorie_vehicule TEXT DEFAULT 'classique',
            marque_vehicule TEXT,
            modele_vehicule TEXT,
            couleur_vehicule TEXT,
            plaque_immatriculation TEXT UNIQUE,
            photo_vehicule_path TEXT,
            courses_effectuees INTEGER DEFAULT 0,
            gains_totaux DECIMAL(10, 2) DEFAULT 0,
            courses_gratuites INTEGER DEFAULT 0,
            compte_suspendu BOOLEAN DEFAULT 0,
            compte_bloque BOOLEAN DEFAULT 0,
            en_attente_verification BOOLEAN DEFAULT 1,
            compte_active BOOLEAN DEFAULT 0,
            latitude REAL,
            longitude REAL,
            disponible BOOLEAN DEFAULT 1,
            en_course BOOLEAN DEFAULT 0,
            avertissements INTEGER DEFAULT 0,
            dernier_avertissement DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # === TABLE : CLIENTS ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telephone TEXT UNIQUE NOT NULL,
            nom TEXT,
            password_hash TEXT NOT NULL,
            email TEXT,
            avertissements_annulation INTEGER DEFAULT 0,
            derniere_annulation DATETIME,
            compte_suspendu BOOLEAN DEFAULT 0,
            date_suspension DATETIME,
            motif_suspension TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # === TABLE : COURSES ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_unique TEXT UNIQUE NOT NULL,
            client_id INTEGER NOT NULL,
            conducteur_id INTEGER,
            depart_lat REAL NOT NULL,
            depart_lng REAL NOT NULL,
            arrivee_lat REAL NOT NULL,
            arrivee_lng REAL NOT NULL,
            distance_km REAL,
            prix_convenu DECIMAL(10, 2) NOT NULL,
            prix_final DECIMAL(10, 2),
            taxes_zahel DECIMAL(10, 2) DEFAULT 0,
            statut TEXT DEFAULT 'en_attente',
            date_demande DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_acceptation DATETIME,
            date_debut DATETIME,
            date_fin DATETIME,
            note_conducteur INTEGER,
            commentaire TEXT,
            paiement_effectue BOOLEAN DEFAULT 0,
            mode_paiement TEXT,
            annule_par TEXT,
            motif_annulation TEXT,
            penalite_appliquee BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id)
        )
        ''')
        
        # === TABLE : CONFIGURATION ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cle TEXT UNIQUE NOT NULL,
            valeur TEXT NOT NULL,
            description TEXT,
            modifiable BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # === TABLE : STATISTIQUES ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistiques (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            courses_jour INTEGER DEFAULT 0,
            courses_semaine INTEGER DEFAULT 0,
            courses_mois INTEGER DEFAULT 0,
            revenus_jour DECIMAL(10, 2) DEFAULT 0,
            revenus_semaine DECIMAL(10, 2) DEFAULT 0,
            revenus_mois DECIMAL(10, 2) DEFAULT 0,
            taxes_dues DECIMAL(10, 2) DEFAULT 0,
            taxes_payees DECIMAL(10, 2) DEFAULT 0,
            amendes_dues DECIMAL(10, 2) DEFAULT 0,
            amendes_payees DECIMAL(10, 2) DEFAULT 0,
            derniere_mise_a_jour DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # === TABLE : LOGS SÉCURITÉ ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs_securite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            utilisateur_type TEXT,
            utilisateur_id INTEGER,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # ========== NOUVELLES TABLES D'AMENDES ==========
        
        # === TABLE : AMENDES ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS amendes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_type TEXT NOT NULL,
            utilisateur_id INTEGER NOT NULL,
            montant DECIMAL(10, 2) NOT NULL,
            raison TEXT NOT NULL,
            statut TEXT DEFAULT 'en_attente',
            date_amende DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_paiement DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (utilisateur_id) REFERENCES clients(id) ON DELETE CASCADE
        )
        ''')
        
        # === TABLE : AVERTISSEMENTS ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS avertissements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_type TEXT NOT NULL,
            utilisateur_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            severite INTEGER DEFAULT 1,
            details TEXT,
            lu BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # === TABLE : SUSPENSIONS ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS suspensions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_type TEXT NOT NULL,
            utilisateur_id INTEGER NOT NULL,
            raison TEXT NOT NULL,
            duree_heures INTEGER,
            date_debut DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_fin DATETIME,
            active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # === TABLE : PHOTOS CONDUCTEUR ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos_conducteur (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conducteur_id INTEGER NOT NULL,
            type_photo TEXT NOT NULL,
            chemin_fichier TEXT NOT NULL,
            valide BOOLEAN DEFAULT 0,
            date_validation DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id) ON DELETE CASCADE
        )
        ''')
        
        # === TABLE : PHOTOS VÉHICULE ===
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos_vehicule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conducteur_id INTEGER NOT NULL,
            type_photo TEXT NOT NULL,
            chemin_fichier TEXT NOT NULL,
            valide BOOLEAN DEFAULT 0,
            date_validation DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id) ON DELETE CASCADE
        )
        ''')
        
        # Insérer les configurations par défaut
        self.insert_default_configs(cursor)
        
        # Insérer l'admin PDG par défaut
        self.insert_default_admin(cursor)
        
        # Insérer les statistiques initiales
        self.insert_default_statistiques(cursor)
        
        conn.commit()
        conn.close()
        
        print("✅ Structure de base créée avec succès!")
    
    def insert_default_configs(self, cursor):
        """Insérer les configurations par défaut"""
        configs = [
            ('app_nom', 'ZAHEL', 'Nom de l\'application'),
            ('app_version', '1.0.0', 'Version de l\'application'),
            ('pourcentage_taxes', '5', 'Pourcentage de taxes ZAHEL (5% = 0.05)'),
            ('seuil_courses', '50', 'Nombre de courses avant bonus'),
            ('duree_annulation_gratuite', '60', 'Durée annulation gratuite (secondes)'),
            ('rayon_disponibilite', '5000', 'Rayon de recherche conducteurs (mètres)'),
            ('amende_annulation', '500', 'Amende pour annulation abusive (KMF)'),
            ('duree_suspension_1', '24', 'Durée 1ère suspension (heures)'),
            ('duree_suspension_2', '72', 'Durée 2ème suspension (heures)'),
            ('seuil_avertissements', '3', 'Seuil d\'avertissements avant suspension'),
            ('compensation_conducteur', '50', 'Pourcentage compensation conducteur client absent'),
            ('duree_attente_max', '10', 'Durée max d\'attente client absent (minutes)')
        ]
        
        for cle, valeur, description in configs:
            cursor.execute('''
                INSERT OR IGNORE INTO configuration (cle, valeur, description)
                VALUES (?, ?, ?)
            ''', (cle, valeur, description))
    
    def insert_default_admin(self, cursor):
        """Insérer l'administrateur PDG par défaut"""
        # Mot de passe: ZAHEL_PDG_2024_CHANGER (à changer immédiatement!)
        password_hash = 'scrypt:32768:8:1$4Qz8W6nX9tR7yP2q$b5c8f...'  # Hash simplifié
        secret_key = 'cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b'
        
        cursor.execute('''
            INSERT OR IGNORE INTO admin_pdg (username, password_hash, email, secret_key)
            VALUES (?, ?, ?, ?)
        ''', ('pdg_zahel', password_hash, 'pdg@zahel.km', secret_key))
    
    def insert_default_statistiques(self, cursor):
        """Insérer les statistiques initiales"""
        cursor.execute('''
            INSERT OR IGNORE INTO statistiques (id) VALUES (1)
        ''')
    
    def get_config(self, cle):
        """Récupérer une configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT valeur FROM configuration WHERE cle = ?', (cle,))
        result = cursor.fetchone()
        conn.close()
        return result['valeur'] if result else None

# Test la base de données
if __name__ == '__main__':
    print("🚀 INITIALISATION BASE DE DONNÉES ZAHEL")
    print("="*50)
    
    db = DatabaseZahel()
    
    print("\n📋 CONFIGURATIONS CHARGÉES:")
    print(f"• Nom application: {db.get_config('app_nom')}")
    print(f"• Taxes: {db.get_config('pourcentage_taxes')}%")
    print(f"• Seuil courses: {db.get_config('seuil_courses')}")
    print(f"• Annulation gratuite: {db.get_config('duree_annulation_gratuite')}s")
    print(f"• Rayon disponibilité: {db.get_config('rayon_disponibilite')}m")
    print(f"• Amende annulation: {db.get_config('amende_annulation')} KMF")
    print(f"• Suspension 1: {db.get_config('duree_suspension_1')}h")
    print(f"• Suspension 2: {db.get_config('duree_suspension_2')}h")
    
    # Compter les tables
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    conn.close()
    
    print(f"\n✅ Base de données prête! {len(tables)} tables créées:")
    for table in tables:
        print(f"   - {table['name']}")
    
    print("\n🔒 Système de sanctions intégré")
    print("💰 Amendes configurées (500 KMF par défaut)")
    print("📊 Statistiques temps réel")
    print("👑 Panel PDG secret")
    print("\n🎉 ZAHEL est prêt pour le système d'amendes!")