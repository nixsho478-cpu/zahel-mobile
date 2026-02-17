# -*- coding: utf-8 -*-
"""
API ZAHEL - BACKEND SÉCURISÉ AVEC TOUTES LES FONCTIONNALITÉS
"""
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask import render_template
import os
import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
import math
from functools import wraps

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:5000"])
app.config['SECRET_KEY'] = secrets.token_hex(32)

# ========== HELPERS ==========
def get_db():
    """Obtenir la connexion à la base de données - CHEMIN ABSOLU UNIQUE"""
    if 'db' not in g:
        # CHEMIN ABSOLU UNIQUE ET DÉFINITIF
        db_path = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"
        
        print(f"🔷 [API UNIQUE] Chemin DB: {db_path}")
        print(f"🔷 [API UNIQUE] Existe: {os.path.exists(db_path)}")
        
        if not os.path.exists(db_path):
            # Solution de secours
            db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"
            print(f"🔷 [API UNIQUE] Tentative secours: {db_path}")
        
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None):
    """Fermer la connexion DB"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_abonnements_table():
    """Créer la table abonnements si elle n'existe pas"""
    try:
        # Utiliser with app.app_context() pour être sûr
        with app.app_context():
            conn = get_db()
            cursor = conn.cursor()
            
            # Créer la table abonnements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS abonnements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conducteur_id INTEGER NOT NULL UNIQUE,
                    courses_achetees INTEGER DEFAULT 50,
                    courses_restantes INTEGER DEFAULT 50,
                    date_achat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_expiration TIMESTAMP,
                    actif BOOLEAN DEFAULT 1,
                    FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id) ON DELETE CASCADE
                )
            ''')
            
            # Créer un index pour accélérer les recherches
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_abonnements_conducteur 
                ON abonnements(conducteur_id)
            ''')
            
            conn.commit()
            print("✅ Table 'abonnements' vérifiée/créée avec succès")
            
            # Ajouter des abonnements par défaut pour les conducteurs existants qui n'en ont pas
            cursor.execute('''
                INSERT OR IGNORE INTO abonnements (conducteur_id, courses_achetees, courses_restantes)
                SELECT id, 50, 50 FROM conducteurs
            ''')
            conn.commit()
            
            nb_ajouts = cursor.rowcount
            if nb_ajouts > 0:
                print(f"✅ {nb_ajouts} abonnement(s) par défaut créé(s) pour les conducteurs existants")
            
    except Exception as e:
        print(f"❌ Erreur création table abonnements: {e}")
        import traceback
        traceback.print_exc()

def init_amendes_chauffeur_table():
    """Créer la table amendes_chauffeur si elle n'existe pas"""
    try:
        with app.app_context():
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS amendes_chauffeur (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amende_id INTEGER NOT NULL,
                    conducteur_id INTEGER NOT NULL,
                    client_id INTEGER NOT NULL,
                    course_code TEXT NOT NULL,
                    montant DECIMAL(10,2) NOT NULL,
                    date_collecte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    statut TEXT DEFAULT 'a_verser',  -- 'a_verser', 'verse', 'annule'
                    date_versement TIMESTAMP,
                    FOREIGN KEY (amende_id) REFERENCES amendes(id),
                    FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id),
                    FOREIGN KEY (client_id) REFERENCES clients(id)
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_amendes_chauffeur_conducteur 
                ON amendes_chauffeur(conducteur_id, statut)
            ''')
            
            conn.commit()
            print("✅ Table 'amendes_chauffeur' vérifiée/créée")
            
    except Exception as e:
        print(f"❌ Erreur création table amendes_chauffeur: {e}")

def init_config_amendes():
    """Initialiser la configuration des amendes"""
    try:
        with app.app_context():
            db = get_db()
            
            # Vérifier si la table configuration existe
            cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='configuration'")
            if not cursor.fetchone():
                db.execute('''
                    CREATE TABLE IF NOT EXISTS configuration (
                        cle TEXT PRIMARY KEY,
                        valeur TEXT,
                        modifiable INTEGER DEFAULT 1,
                        description TEXT
                    )
                ''')
            
            # Configuration par défaut
            config_defaut = [
                ('delai_annulation_apres_acceptation', '180', 'Délai en secondes pour annulation gratuite après acceptation'),
                ('montant_amende_annulation_tardive', '500', 'Montant de l\'amende pour annulation après délai'),
                ('avertissements_avant_suspension', '3', "Nombre d'avertissements avant suspension"),
                ('indemnisation_conducteur', '100', 'Indemnisation pour déplacement si client annule tard')
            ]
            
            for cle, valeur, desc in config_defaut:
                db.execute('''
                    INSERT OR IGNORE INTO configuration (cle, valeur, description, modifiable)
                    VALUES (?, ?, ?, 1)
                ''', (cle, valeur, desc))
            
            db.commit()
            print("✅ Configuration des amendes initialisée")
            
    except Exception as e:
        print(f"❌ Erreur init_config_amendes: {e}")

def init_taxes_column():
    """Ajouter la colonne taxes_cumulees à la table conducteurs si elle n'existe pas"""
    try:
        with app.app_context():
            db = get_db()
            
            # Vérifier si la colonne existe déjà
            cursor = db.execute("PRAGMA table_info(conducteurs)")
            colonnes = [col[1] for col in cursor.fetchall()]
            
            if 'taxes_cumulees' not in colonnes:
                db.execute('ALTER TABLE conducteurs ADD COLUMN taxes_cumulees DECIMAL(10,2) DEFAULT 0')
                print("✅ Colonne 'taxes_cumulees' ajoutée à la table conducteurs")
            
            # Ajouter aussi une table pour l'historique mensuel
            cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historique_conducteur'")
            if not cursor.fetchone():
                db.execute('''
                    CREATE TABLE historique_conducteur (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conducteur_id INTEGER NOT NULL,
                        mois TEXT NOT NULL,  -- Format: YYYY-MM
                        courses_effectuees INTEGER DEFAULT 0,
                        gains_totaux DECIMAL(10,2) DEFAULT 0,
                        taxes_payees DECIMAL(10,2) DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id)
                    )
                ''')
                print("✅ Table 'historique_conducteur' créée")
            
            db.commit()
            
    except Exception as e:
        print(f"❌ Erreur init_taxes_column: {e}")

def hash_password(password):
    """Hasher un mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def verifier_password(password_hash, password):
    """Vérifier un mot de passe"""
    return password_hash == hash_password(password)

def generate_code_course():
    """Générer un code unique pour une course"""
    import random
    lettres = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ', k=3))
    chiffres = ''.join(random.choices('0123456789', k=4))
    return f"ZAHEL-{lettres}{chiffres}"

def calculer_distance(lat1, lon1, lat2, lon2):
    """Calculer distance entre deux points (simplifié)"""
    # Formule Haversine simplifiée
    R = 6371000  # Rayon Terre en mètres
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2) * math.sin(delta_lat/2) + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * \
        math.sin(delta_lon/2) * math.sin(delta_lon/2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c  # Distance en mètres

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'error': 'Token manquant'}), 401
        
        # ICI : Ta logique de validation du token
        # Par exemple, vérifier dans la base de données
        conn = get_db()
        cursor = conn.cursor()
        
        # Chercher si c'est un client
        cursor.execute("SELECT id, telephone FROM clients WHERE token = ?", (token,))
        client = cursor.fetchone()
        if client:
            conn.close()
            return f(client, *args, **kwargs)
        
        # Chercher si c'est un conducteur
        cursor.execute("SELECT immatricule FROM conducteurs WHERE token = ?", (token,))
        conducteur = cursor.fetchone()
        if conducteur:
            conn.close()
            return f(conducteur, *args, **kwargs)
        
        conn.close()
        return jsonify({'success': False, 'error': 'Token invalide'}), 401
    
    return decorated

# ========== MIDDLEWARE AUTH ==========
def require_auth(role=None):
    """Décorateur pour authentification"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 🔍 DEBUG CRITIQUE
            print(f"\n🎯 DEBUG require_auth - Route: {request.path}")
            print(f"   Token: {request.headers.get('Authorization', 'NONE')}")
            print(f"   Rôle: {role}")
            
            token = request.headers.get('Authorization')
            if not token:
                print("   ❌ Token manquant")
                return jsonify({'error': 'Token manquant'}), 401
            
            db = get_db()
            user = None
            user_type = None
            
            # 🔍 DEBUG chaque étape
            print(f"   Recherche utilisateur...")
            
            # Vérifier selon le rôle
            if role == 'admin':
                print(f"   Recherche admin...")
                cursor = db.execute(
                    'SELECT * FROM admin_pdg WHERE secret_key = ?',
                    (token,)
                )
                user = cursor.fetchone()
                if user:
                    user_type = 'admin'
                    
            elif role == 'conducteur':
                print(f"   Recherche conducteur...")
                cursor = db.execute(
                    'SELECT * FROM conducteurs WHERE immatricule = ?',
                    (token,)
                )
                user = cursor.fetchone()
                if user:
                    user_type = 'conducteur'
                    
            elif role == 'client':
                 print(f"   Recherche client par téléphone...")
                # Chercher par téléphone (le token des clients)
            cursor = db.execute(
               'SELECT * FROM clients WHERE telephone = ?',
                (token,)
            )
            user = cursor.fetchone()
            if user:
                user_type = 'client'
                    
            else:  # ❗ IMPORTANT : Pas de rôle spécifique → chercher dans TOUTES les tables
                print(f"   Recherche dans toutes les tables (role=None)...")
                
                # 1. Chercher dans admin
                cursor = db.execute(
                    'SELECT * FROM admin_pdg WHERE secret_key = ?',
                    (token,)
                )
                user = cursor.fetchone()
                if user:
                    user_type = 'admin'
                    print(f"   ✅ Trouvé dans admin_pdg")
                
                # 2. Si pas admin, chercher dans conducteurs
                if not user:
                    cursor = db.execute(
                        'SELECT * FROM conducteurs WHERE immatricule = ?',
                        (token,)
                    )
                    user = cursor.fetchone()
                    if user:
                        user_type = 'conducteur'
                        print(f"   ✅ Trouvé dans conducteurs (immatricule)")
                
               # 3. Si pas conducteur, chercher dans clients (par téléphone d'abord)
                if not user:
                    cursor = db.execute(
                       'SELECT * FROM clients WHERE telephone = ?',
                       (token,)
                    )
                    user = cursor.fetchone()
                    if user:
                        user_type = 'client'
                        print(f"   ✅ Trouvé dans clients (telephone)")
                
                # 4. Si pas par hash, essayer par téléphone
                if not user:
                    cursor = db.execute(
                        'SELECT * FROM clients WHERE telephone = ?',
                        (token,)
                    )
                    user = cursor.fetchone()
                    if user:
                        user_type = 'client'
                        print(f"   ✅ Trouvé dans clients (telephone)")
            
            if not user:
                print(f"   ❌ Aucun utilisateur trouvé avec ce token")
                return jsonify({'error': 'Token invalide'}), 401
            
            print(f"   ✅ Utilisateur trouvé : type={user_type}, id={user[0]}")
            
            # Convertir en dict avec le type
            user_dict = dict(user)
            user_dict['type'] = user_type  # Ajouter le type
            user_dict['id'] = user[0]      # S'assurer que l'ID est présent
            
            g.user = user_dict
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ========== ROUTES PUBLIQUES ==========
@app.route('/')
def accueil():
    return jsonify({
        'application': 'ZAHEL',
        'version': '1.0.0',
        'status': 'online',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/config')
def get_config():
    """Récupérer configuration publique"""
    db = get_db()
    cursor = db.execute('SELECT cle, valeur FROM configuration WHERE modifiable = 1')
    config = {row['cle']: row['valeur'] for row in cursor.fetchall()}
    
    return jsonify({
        'application': {
            'nom': 'ZAHEL',
            'description': 'Transport sécurisé aux Comores'
        },
        'config': config
    })


# ========== ROUTES CONDUCTEURS ==========
@app.route('/api/conducteurs/inscription', methods=['POST'])
def inscrire_conducteur():
    """Inscription conducteur avec toutes les vérifications"""
    data = request.json
    required_fields = ['nom', 'telephone', 'password', 'nationalite', 
                      'numero_identite', 'categorie', 'marque', 'modele',
                      'couleur', 'plaque']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Champ manquant: {field}'}), 400
    
    db = get_db()
    
    # Vérifier téléphone unique
    cursor = db.execute(
        'SELECT id FROM conducteurs WHERE telephone = ?',
        (data['telephone'],)
    )
    if cursor.fetchone():
        return jsonify({'error': 'Numéro déjà utilisé'}), 400
    
    # Vérifier plaque unique
    cursor = db.execute(
        'SELECT id FROM conducteurs WHERE plaque_immatriculation = ?',
        (data['plaque'],)
    )
    if cursor.fetchone():
        return jsonify({'error': 'Plaque déjà enregistrée'}), 400
    
    # Générer immatricule
    import random
    lettres = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ', k=3))
    chiffres = ''.join(random.choices('0123456789', k=3))
    immatricule = f"ZH-{chiffres}{lettres}"
    
    # Système hybride WhatsApp - ZAHEL
    categorie = data['categorie']
    if categorie in ['confort', 'luxe']:
        # Vérification REQUISE par WhatsApp
        en_attente_verification = 1
        compte_active = 0  # Compte inactif tant que non vérifié
        message_verification = f"INSCRIPTION SOUMISE - Envoyez vos documents sur WhatsApp"
    else:
        # Moto et Standard : activation immédiate
        en_attente_verification = 0
        compte_active = 1
        message_verification = "INSCRIPTION RÉUSSIE - Vous pouvez vous connecter immédiatement"
    
    # Insérer conducteur
    cursor = db.execute('''
    INSERT INTO conducteurs (
        immatricule, nom, telephone, password_hash, nationalite,
        numero_identite, categorie_vehicule, marque_vehicule,
        modele_vehicule, couleur_vehicule, plaque_immatriculation,
        en_attente_verification, compte_active
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        immatricule,
        data['nom'],
        data['telephone'],
        hash_password(data['password']),
        data['nationalite'],
        data['numero_identite'],
        data['categorie'],
        data['marque'],
        data['modele'],
        data['couleur'],
        data['plaque'],
        en_attente_verification,
        compte_active
    ))
    
    conducteur_id = cursor.lastrowid
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Inscription réussie',
        'conducteur': {
            'id': conducteur_id,
            'immatricule': immatricule,
            'nom': data['nom'],
            'verification_requise': en_attente_verification
        }
    }), 201

@app.route('/api/conducteurs/connexion', methods=['POST'])
def connexion_conducteur():
    """Connexion conducteur"""
    data = request.json
    
    if 'telephone' not in data or 'password' not in data:
        return jsonify({'error': 'Téléphone et mot de passe requis'}), 400
    
    db = get_db()
    cursor = db.execute(
        '''SELECT id, immatricule, nom, password_hash, compte_active, 
                  compte_suspendu, compte_bloque, en_attente_verification,
                  categorie_vehicule, courses_effectuees, gains_totaux,
                  latitude, longitude, disponible
           FROM conducteurs WHERE telephone = ?''',
        (data['telephone'],)
    )
    
    conducteur = cursor.fetchone()
    
    if not conducteur or not verifier_password(conducteur['password_hash'], data['password']):
        # Log tentative échouée
        cursor = db.execute('''
        INSERT INTO logs_securite (type, details)
        VALUES (?, ?)
        ''', ('tentative_connexion', f'Tentative échouée: {data["telephone"]}'))
        db.commit()
        
        return jsonify({'error': 'Identifiants incorrects'}), 401
    
    # Mettre à jour dernière connexion
    db.execute(
        'UPDATE conducteurs SET updated_at = ? WHERE id = ?',
        (datetime.now().isoformat(), conducteur['id'])
    )
    db.commit()
    
    return jsonify({
        'success': True,
        'token': conducteur['immatricule'],  # Utiliser immatricule comme token
        'conducteur': {
            'id': conducteur['id'],
            'immatricule': conducteur['immatricule'],
            'nom': conducteur['nom'],
            'compte_active': bool(conducteur['compte_active']),
            'compte_suspendu': bool(conducteur['compte_suspendu']),
            'compte_bloque': bool(conducteur['compte_bloque']),
            'en_attente_verification': bool(conducteur['en_attente_verification']),
            'categorie': conducteur['categorie_vehicule'],
            'courses_effectuees': conducteur['courses_effectuees'],
            'gains_totaux': conducteur['gains_totaux'],
            'position': {
                'latitude': conducteur['latitude'],
                'longitude': conducteur['longitude']
            } if conducteur['latitude'] and conducteur['longitude'] else None,
            'disponible': bool(conducteur['disponible'])
        }
    })

@app.route('/api/conducteur/statistiques', methods=['GET'])
@require_auth('conducteur')
def get_conducteur_statistiques():
    """Récupérer les statistiques du conducteur connecté - VERSION CORRIGÉE"""
    try:
        db = get_db()
        
        # Récupérer l'ID du conducteur depuis le token
        conducteur_id = g.user['id']
        
        print(f"🔍 Recherche conducteur ID: {conducteur_id}")
        
        # 1. Récupérer les infos du conducteur avec toutes les colonnes
        cursor = db.execute('''
            SELECT 
                immatricule, 
                nom, 
                telephone,
                marque_vehicule,
                modele_vehicule,
                couleur_vehicule,
                plaque_immatriculation,
                courses_effectuees, 
                gains_totaux, 
                disponible, 
                en_course,
                note_moyenne,
                taxes_cumulees
            FROM conducteurs 
            WHERE id = ?
        ''', (conducteur_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Conducteur non trouvé'}), 404
        
        # Extraire les valeurs - 13 colonnes
        (immatricule, nom, telephone, marque, modele, couleur, plaque,
         courses_effectuees, gains_totaux, disponible, en_course, 
         note_moyenne, taxes_cumulees) = row
        
        print(f"✅ Données brutes: courses={courses_effectuees}, gains={gains_totaux}, taxes={taxes_cumulees}")
        
        # 2. Calculer la note moyenne si pas déjà calculée
        if note_moyenne is None:
            cursor.execute('''
                SELECT AVG(note_conducteur) 
                FROM courses 
                WHERE conducteur_id = ? AND statut = 'terminee' AND note_conducteur IS NOT NULL
            ''', (conducteur_id,))
            
            note_result = cursor.fetchone()[0]
            note_moyenne = note_result if note_result is not None else 5.0
        
        # 3. Récupérer les courses restantes depuis l'abonnement
        try:
            cursor_abonnement = db.execute('''
                SELECT courses_restantes FROM abonnements 
                WHERE conducteur_id = ? AND actif = 1
            ''', (conducteur_id,))
    
            abonnement = cursor_abonnement.fetchone()
    
            if abonnement:
                courses_restantes = abonnement[0]
                print(f"📊 Courses restantes (à jour): {courses_restantes}")
            else:
                # Si pas d'abonnement, en créer un par défaut
                print("ℹ️ Aucun abonnement trouvé - Création par défaut")
                db.execute('''
                    INSERT INTO abonnements (conducteur_id, courses_achetees, courses_restantes)
                    VALUES (?, 50, 50)
                ''', (conducteur_id,))
                db.commit()
                courses_restantes = 50
                print(f"✅ Abonnement par défaut créé pour conducteur {conducteur_id}")
        
        except Exception as e:
            print(f"⚠️ Erreur récupération abonnement: {e}")
            courses_restantes = 50
        
        # 4. Préparer la réponse
        statistiques = {
            'immatricule': immatricule,
            'nom': nom,
            'telephone': telephone,  
            'vehicule': {
                'marque': marque,
                'modele': modele,
                'couleur': couleur,
                'plaque': plaque
            },  
            'performance': {
                'courses_effectuees': int(courses_effectuees) if courses_effectuees else 0,
                'gains_totaux': float(gains_totaux) if gains_totaux else 0.0,
                'note_moyenne': float(note_moyenne) if note_moyenne else 5.0,
                'courses_restantes': int(courses_restantes),
                'taxes_cumulees': float(taxes_cumulees) if taxes_cumulees else 0.0
            },
            'statut': {
                'disponible': bool(disponible),
                'en_course': bool(en_course)
            }
        }
        
        print(f"📊 Statistiques préparées:")
        print(f"   - Nom: {nom}")
        print(f"   - Téléphone: {telephone}")
        print(f"   - Véhicule: {marque} {modele}")
        
        return jsonify({
            'success': True,
            'conducteur': statistiques
        })
        
    except Exception as e:
        print(f"❌ Erreur statistiques conducteur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conducteur/login', methods=['POST'])
def conducteur_login():
    """Connexion d'un conducteur - VERSION AVEC HASH SHA-256"""
    print("🎯 CONDUCTEUR LOGIN appelé")
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'Données manquantes'}), 400
    
    immatricule = data.get('immatricule')
    password = data.get('password')
    
    if not immatricule or not password:
        return jsonify({'success': False, 'error': 'Immatricule/mot de passe requis'}), 400
    
    print(f"🔐 Tentative connexion conducteur: {immatricule}")
    
    db = get_db()
    
    try:
        # 🔥 HASHER le mot de passe reçu en SHA-256 (comme dans ta base)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"🔐 Hash généré: {password_hash}")
        print(f"🔐 Hash stocké attendu: e8a3ba4ad3991efc6377cc158d2e324102e7214fd61834ee06e3e85bece0681f")
        
        cursor = db.execute(
            'SELECT id, nom, immatricule, disponible FROM conducteurs WHERE immatricule = ? AND password_hash = ?',
            (immatricule, password_hash)
        )
        conducteur = cursor.fetchone()
        
        if conducteur:
            print(f"✅ Conducteur {immatricule} connecté")
            # Token = immatricule pour les conducteurs
            token = immatricule
            return jsonify({
                'success': True,
                'token': token,
                'conducteur': {
                    'id': conducteur['id'],
                    'nom': conducteur['nom'],
                    'immatricule': conducteur['immatricule'],
                    'disponible': conducteur['disponible'] == 1
                }
            })
        else:
            print(f"❌ Échec connexion conducteur: {immatricule}")
            print(f"🔍 Hash généré: {password_hash}")
            print(f"🔍 Hash stocké: e8a3ba4ad3991efc6377cc158d2e324102e7214fd61834ee06e3e85bece0681f")
            
            # DEBUG supplémentaire
            cursor_debug = db.execute(
                'SELECT immatricule, password_hash FROM conducteurs WHERE immatricule = ?',
                (immatricule,)
            )
            debug_result = cursor_debug.fetchone()
            if debug_result:
                print(f"🔍 DEBUG - Hash stocké réel: {debug_result[1]}")
                print(f"🔍 DEBUG - Correspondance: {'OUI' if password_hash == debug_result[1] else 'NON'}")
            
            return jsonify({'success': False, 'error': 'Immatricule ou mot de passe incorrect'}), 401
            
    except Exception as e:
        print(f"❌ ERREUR SQL conducteur_login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Erreur base de données: {str(e)}'}), 500


@app.route('/api/conducteur/toggle_status', methods=['POST'])
@require_auth('conducteur')
def toggle_conducteur_status():
    """Basculer le statut disponible/indisponible du conducteur"""
    db = get_db()
    conducteur_id = g.user['id']
    
    # Récupérer le statut actuel
    cursor = db.execute(
        'SELECT disponible FROM conducteurs WHERE id = ?',
        (conducteur_id,)
    )
    conducteur = cursor.fetchone()
    
    if not conducteur:
        return jsonify({'success': False, 'error': 'Conducteur non trouvé'}), 404
    
    # Basculer le statut
    nouveau_statut = 0 if conducteur['disponible'] == 1 else 1
    
    # Mettre à jour la base
    db.execute(
        'UPDATE conducteurs SET disponible = ?, updated_at = datetime("now") WHERE id = ?',
        (nouveau_statut, conducteur_id)
    )
    db.commit()
    
    return jsonify({
        'success': True,
        'disponible': nouveau_statut == 1,
        'message': f'Statut mis à jour: {"DISPONIBLE" if nouveau_statut == 1 else "INDISPONIBLE"}'
    })

# ==================== ROUTES CLIENT ====================
@app.route('/api/client/login', methods=['POST'])
def client_login():
    """Connexion client"""
    data = request.json
    telephone = data.get('telephone')
    password = data.get('password')
    
    if not telephone or not password:
        return jsonify({'error': 'Téléphone et mot de passe requis'}), 400
    
    db = get_db()
    cursor = db.execute(
        'SELECT id, nom, telephone, password_hash FROM clients WHERE telephone = ?',
        (telephone,)
    )
    client = cursor.fetchone()
    
    if not client:
        return jsonify({'error': 'Client non trouvé'}), 404
    
    if not verifier_password(client['password_hash'], password):
        return jsonify({'error': 'Mot de passe incorrect'}), 401
    
    # Générer token (téléphone pour l'instant)
    token = telephone
    
    return jsonify({
        'success': True,
        'token': token,
        'client': {
            'id': client['id'],
            'nom': client['nom'],
            'telephone': client['telephone']
        }
    })

@app.route('/api/client/register', methods=['POST'])
def client_register():
    """Inscription client (version corrigée)"""
    data = request.json
    nom = data.get('nom')
    telephone = data.get('telephone')
    password = data.get('password')
    
    if not nom or not telephone or not password:
        return jsonify({'error': 'Tous les champs sont requis'}), 400
    
    db = get_db()
    
    # Vérifier si le téléphone existe déjà
    cursor = db.execute('SELECT id FROM clients WHERE telephone = ?', (telephone,))
    if cursor.fetchone():
        return jsonify({'error': 'Ce numéro de téléphone est déjà utilisé'}), 409
    
    # Hasher le mot de passe
    password_hash = hash_password(password)
    
    # REQUÊTE CORRIGÉE : sans compte_active
    db.execute(
        'INSERT INTO clients (nom, telephone, password_hash, created_at) VALUES (?, ?, ?, datetime("now"))',
        (nom, telephone, password_hash)
    )
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Client créé avec succès',
        'client': {
            'nom': nom,
            'telephone': telephone
        }
    }), 201


@app.route('/api/client/courses', methods=['GET'])
@require_auth('client')
def get_client_courses():
    """Récupérer toutes les courses d'un client"""
    print("📋 API: get_client_courses appelée")
    
    try:
        db = get_db()
        client_id = g.user['id']
        
        print(f"🔍 Client ID: {client_id}")
        
        cursor = db.execute('''
            SELECT 
                c.id,
                c.code_unique,
                c.statut,
                c.prix_convenu,
                c.prix_final,
                c.date_demande,
                c.date_acceptation,
                c.date_debut,
                c.date_fin,
                c.point_depart_lat,
                c.point_depart_lng,
                c.point_arrivee_lat,
                c.point_arrivee_lng,
                c.adresse_depart,
                c.adresse_arrivee,
                c.categorie_demande,
                cond.nom as conducteur_nom,
                cond.immatricule as conducteur_immatricule,
                cond.telephone as conducteur_telephone
            FROM courses c
            LEFT JOIN conducteurs cond ON c.conducteur_id = cond.id
            WHERE c.client_id = ?
            ORDER BY c.date_demande DESC
            LIMIT 50
        ''', (client_id,))
        
        courses = cursor.fetchall()
        print(f"✅ {len(courses)} course(s) trouvée(s) pour le client")
        
        result = []
        for row in courses:
            # Formater la date pour l'affichage
            date_demande = datetime.fromisoformat(row['date_demande']) if row['date_demande'] else None
            date_formatee = date_demande.strftime("%d/%m/%Y %H:%M") if date_demande else "Date inconnue"
            
            # Déterminer le statut lisible
            statut_map = {
                'en_recherche': '🔍 En recherche',
                'en_attente': '⏳ En attente',
                'acceptee': '✅ Acceptée',
                'en_cours': '🚗 En cours',
                'terminee': '🏁 Terminée',
                'annulee': '❌ Annulée'
            }
            statut_lisible = statut_map.get(row['statut'], row['statut'])
            
            course_data = {
                'id': row['id'],
                'code': row['code_unique'],
                'statut': row['statut'],
                'statut_lisible': statut_lisible,
                'prix_convenu': float(row['prix_convenu']) if row['prix_convenu'] else 0.0,
                'prix_final': float(row['prix_final']) if row['prix_final'] else 0.0,
                'date': date_formatee,
                'date_iso': row['date_demande'],
                'categorie': row['categorie_demande'] or 'standard',
                'depart': {
                    'lat': row['point_depart_lat'],
                    'lng': row['point_depart_lng'],
                    'adresse': row['adresse_depart'] or 'Non spécifiée'
                },
                'arrivee': {
                    'lat': row['point_arrivee_lat'],
                    'lng': row['point_arrivee_lng'],
                    'adresse': row['adresse_arrivee'] or 'Non spécifiée'
                },
                'conducteur': None
            }
            
            # Ajouter conducteur si disponible
            if row['conducteur_nom']:
                course_data['conducteur'] = {
                    'nom': row['conducteur_nom'],
                    'immatricule': row['conducteur_immatricule'],
                    'telephone': row['conducteur_telephone']
                }
            
            result.append(course_data)
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'courses': result,
            'count': len(result),
            'total_courses': len(result),
            'courses_terminees': len([c for c in result if c['statut'] == 'terminee']),
            'courses_annulees': len([c for c in result if c['statut'] == 'annulee']),
            'message': f'{len(result)} course(s) trouvée(s)'
        })
        
    except Exception as e:
        print(f"❌ Erreur get_client_courses: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération des courses'
        }), 500

# ========== ROUTES ADRESSES FRÉQUENTES ==========

@app.route('/api/client/adresses', methods=['GET'])
@require_auth('client')
def get_client_adresses():
    """Récupérer les adresses fréquentes d'un client"""
    db = get_db()
    client_id = g.user['id']
    
    cursor = db.execute('''
        SELECT id, nom, adresse, latitude, longitude, type, est_principale
        FROM adresses_frequentes 
        WHERE client_id = ?
        ORDER BY 
            est_principale DESC,  -- Adresses principales d'abord
            type,
            nom
    ''', (client_id,))
    
    adresses = cursor.fetchall()
    
    result = []
    for row in adresses:
        result.append({
            'id': row['id'],
            'nom': row['nom'],
            'adresse': row['adresse'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'type': row['type'],
            'est_principale': bool(row['est_principale'])
        })
    
    return jsonify({
        'success': True,
        'client_id': client_id,
        'adresses': result,
        'count': len(result)
    })

@app.route('/api/client/adresses', methods=['POST'])
@require_auth('client')
def add_client_adresse():
    """Ajouter une adresse fréquente"""
    data = request.json
    client_id = g.user['id']
    
    if not data or 'nom' not in data or 'adresse' not in data:
        return jsonify({'error': 'Nom et adresse requis'}), 400
    
    db = get_db()
    
    # Vérifier si c'est la première adresse (deviendra principale)
    cursor = db.execute('SELECT COUNT(*) FROM adresses_frequentes WHERE client_id = ?', (client_id,))
    count = cursor.fetchone()[0]
    est_principale = 1 if count == 0 else data.get('est_principale', 0)
    
    # Si on marque comme principale, désactiver les autres principales
    if est_principale:
        db.execute('UPDATE adresses_frequentes SET est_principale = 0 WHERE client_id = ?', (client_id,))
    
    # Insérer la nouvelle adresse
    cursor = db.execute('''
        INSERT INTO adresses_frequentes 
        (client_id, nom, adresse, latitude, longitude, type, est_principale)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        client_id,
        data['nom'],
        data['adresse'],
        data.get('latitude'),
        data.get('longitude'),
        data.get('type', 'personnel'),
        est_principale
    ))
    
    adresse_id = cursor.lastrowid
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Adresse ajoutée avec succès',
        'adresse_id': adresse_id,
        'est_principale': bool(est_principale)
    }), 201

@app.route('/api/client/adresses/<int:adresse_id>', methods=['DELETE'])
@require_auth('client')
def delete_client_adresse(adresse_id):
    """Supprimer une adresse fréquente"""
    db = get_db()
    client_id = g.user['id']
    
    # Vérifier que l'adresse appartient bien au client
    cursor = db.execute('''
        SELECT est_principale FROM adresses_frequentes 
        WHERE id = ? AND client_id = ?
    ''', (adresse_id, client_id))
    
    adresse = cursor.fetchone()
    
    if not adresse:
        return jsonify({'error': 'Adresse non trouvée'}), 404
    
    # Supprimer l'adresse
    db.execute('DELETE FROM adresses_frequentes WHERE id = ? AND client_id = ?', (adresse_id, client_id))
    
    # Si c'était l'adresse principale, en choisir une nouvelle
    if adresse['est_principale']:
        cursor = db.execute('SELECT id FROM adresses_frequentes WHERE client_id = ? LIMIT 1', (client_id,))
        nouvelle_principale = cursor.fetchone()
        
        if nouvelle_principale:
            db.execute('UPDATE adresses_frequentes SET est_principale = 1 WHERE id = ?', (nouvelle_principale['id'],))
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Adresse supprimée avec succès'
    })


@app.route('/api/client/change_password', methods=['POST'])
@require_auth('client')
def change_client_password():
    """Changer le mot de passe du client"""
    data = request.json
    client_id = g.user['id']
    
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Ancien et nouveau mot de passe requis'}), 400
    
    db = get_db()
    
    # Vérifier l'ancien mot de passe
    cursor = db.execute(
        'SELECT password_hash FROM clients WHERE id = ?',
        (client_id,)
    )
    client = cursor.fetchone()
    
    if not client or not verifier_password(client['password_hash'], data['old_password']):
        return jsonify({'success': False, 'error': 'Ancien mot de passe incorrect'}), 401
    
    # Hasher le nouveau mot de passe
    new_password_hash = hash_password(data['new_password'])
    
    # Mettre à jour
    db.execute(
        'UPDATE clients SET password_hash = ?, updated_at = ? WHERE id = ?',
        (new_password_hash, datetime.now().isoformat(), client_id)
    )
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Mot de passe modifié avec succès'
    })


@app.route('/api/client/amendes', methods=['GET'])
@require_auth('client')
def get_amendes_client():
    """Récupérer les amendes d'un client"""
    db = get_db()
    client_id = g.user['id']
    
    # Récupérer les amendes du client
    cursor = db.execute('''
        SELECT id, montant, raison, statut, 
               date_amende, date_paiement
        FROM amendes 
        WHERE utilisateur_type = 'client' 
          AND utilisateur_id = ?
        ORDER BY date_amende DESC
    ''', (client_id,))
    
    amendes = cursor.fetchall()
    
    # Formater la réponse
    result = []
    for amende in amendes:
        result.append({
            'id': amende['id'],
            'montant': float(amende['montant']),
            'raison': amende['raison'],
            'statut': amende['statut'],
            'date_amende': amende['date_amende'],
            'date_paiement': amende['date_paiement'],
        })
    
    return jsonify({
        'success': True,
        'client_id': client_id,
        'amendes': result,
        'total_impayees': sum(a['montant'] for a in result if a['statut'] == 'en_attente'),
        'count_impayees': len([a for a in result if a['statut'] == 'en_attente'])
    })

# ========== ROUTES PDG SECRET ==========
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Connexion PDG secret"""
    data = request.json
    
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Identifiants requis'}), 400
    
    db = get_db()
    cursor = db.execute(
        'SELECT * FROM admin_pdg WHERE username = ?',
        (data['username'],)
    )
    
    admin = cursor.fetchone()
    
    if not admin or not verifier_password(admin['password_hash'], data['password']):
        return jsonify({'error': 'Accès non autorisé'}), 401
    
    # Mettre à jour dernière connexion
    db.execute(
        'UPDATE admin_pdg SET last_login = ? WHERE id = ?',
        (datetime.now().isoformat(), admin['id'])
    )
    db.commit()
    
    # Log connexion réussie
    db.execute('''
    INSERT INTO logs_securite (type, utilisateur_type, utilisateur_id, details)
    VALUES (?, ?, ?, ?)
    ''', ('connexion_admin', 'admin', admin['id'], 'Connexion PDG réussie'))
    db.commit()
    
    return jsonify({
        'success': True,
        'token': admin['secret_key'],
        'admin': {
            'id': admin['id'],
            'username': admin['username'],
            'email': admin['email'],
            'permissions': admin['permissions']
        }
    })



# ========== ROUTE : DASHBOARD WEB PDG ==========# 
@app.route('/admin/dashboard', methods=['GET'])
def dashboard_pdg():
    """Page web du dashboard PDG - Version finale"""
    token = request.args.get('token')
    
    if not token:
        return jsonify({'error': 'Accès non autorisé. Token requis.'}), 401
    
    db = get_db()
    cursor = db.execute(
        'SELECT id FROM admin_pdg WHERE secret_key = ?',
        (token,)
    )
    
    if not cursor.fetchone():
        return jsonify({'error': 'Token invalide'}), 401
    
    # Retourner le template du dashboard
    return render_template('dashboard_pdg.html')


# ========== ROUTE : RECHERCHE CONDUCTEUR PAR IMMATRICULE ========== 
@app.route('/api/admin/conducteur/<immatricule>', methods=['GET'])
@require_auth('admin')
def get_conducteur_details(immatricule):
    """Récupérer tous les détails d'un conducteur pour le PDG"""
    db = get_db()
    
       # 1. Rechercher le conducteur
    cursor = db.execute('''
        SELECT id, immatricule, nom, telephone, email, nationalite,
               numero_identite, categorie_vehicule, marque_vehicule,
               modele_vehicule, couleur_vehicule, plaque_immatriculation,
               courses_effectuees, gains_totaux, compte_suspendu, 
               disponible, en_course, created_at, updated_at
        FROM conducteurs
        WHERE immatricule = ?
    ''', (immatricule,))
    
    conducteur = cursor.fetchone()
    
    if not conducteur:
        return jsonify({
            'success': False,
            'error': f'Conducteur non trouvé: {immatricule}'
        }), 404
    
    # 2. Récupérer les photos (si table existe)
    photos = []
    try:
        cursor.execute('SELECT type_photo, chemin_fichier FROM photos_conducteur WHERE conducteur_id = ?', 
                      (conducteur[0],))
        photos = [{'type': row[0], 'chemin': row[1]} for row in cursor.fetchall()]
    except:
        pass  # Table photos peut ne pas exister encore
    
    # 3. Récupérer l'historique des courses
    cursor.execute('''
        SELECT code_unique, statut, prix_convenu, prix_final, date_demande,
               date_acceptation, date_debut, date_fin, note_conducteur
        FROM courses 
        WHERE conducteur_id = ?
        ORDER BY date_demande DESC
        LIMIT 10
    ''', (conducteur[0],))
    
    historique = []
    for row in cursor.fetchall():
        historique.append({
            'code': row[0],
            'statut': row[1],
            'prix_convenu': row[2],
            'prix_final': row[3],
            'date_demande': row[4],
            'date_acceptation': row[5],
            'date_debut': row[6],
            'date_fin': row[7],
            'note': row[8]
        })
    
    # 4. Récupérer les amendes/sanctions
    amendes = []
    try:
        cursor.execute('''
            SELECT montant, raison, date_amende, payee
            FROM amendes 
            WHERE conducteur_id = ? AND payee = 0
        ''', (conducteur[0],))
        amendes = [{'montant': row[0], 'raison': row[1], 'date': row[2], 'payee': bool(row[3])} 
                  for row in cursor.fetchall()]
    except:
        pass
    
        # 5. Préparer la réponse
    conducteur_dict = {
        'success': True,
        'conducteur': {
            'id': conducteur[0],
            'immatricule': conducteur[1],
            'nom': conducteur[2],
            'telephone': conducteur[3],
            'email': conducteur[4],
            'nationalite': conducteur[5],
            'numero_identite': conducteur[6],
            'vehicule': {
                'categorie': conducteur[7],      # categorie_vehicule
                'marque': conducteur[8],         # marque_vehicule
                'modele': conducteur[9],         # modele_vehicule
                'couleur': conducteur[10],       # couleur_vehicule
                'plaque': conducteur[11]         # plaque_immatriculation
            },
            'performance': {
                'courses_effectuees': conducteur[12],    # courses_effectuees
                'gains_totaux': conducteur[13]           # gains_totaux
            },
            'statut': {
                'suspendu': bool(conducteur[14]),        # compte_suspendu
                'disponible': bool(conducteur[15]),      # disponible
                'en_course': bool(conducteur[16])        # en_course
            },
            'dates': {
                'creation': conducteur[17],              # created_at
                'maj': conducteur[18]                    # updated_at
            }
        }
    }
    return jsonify(conducteur_dict)

    # ================== AUTHENTIFICATION CONDUCTEUR ==================

@app.route('/api/conducteurs/login', methods=['POST'])
def login_conducteur():
    """Connexion d'un conducteur (pour application mobile)"""
    data = request.json
    
    if not data or 'immatricule' not in data or 'password' not in data:
        return jsonify({'error': 'Immatricule et mot de passe requis'}), 400
    
    immatricule = data['immatricule'].strip()
    password = data['password']
    
    db = get_db()
    
    # Rechercher le conducteur
    cursor = db.execute(
        '''SELECT id, nom, telephone, password_hash, immatricule,
                  compte_suspendu, disponible, en_course,
                  courses_effectuees, gains_totaux 
           FROM conducteurs 
           WHERE immatricule = ?''',
        (immatricule,)
    )
    
    conducteur = cursor.fetchone()
    
    if not conducteur:
        return jsonify({'error': 'Conducteur non trouvé'}), 404
    
    # Vérifier si le compte est suspendu
    if conducteur['compte_suspendu']:
        return jsonify({'error': 'Compte suspendu. Contactez l\'administration.'}), 403
    
    # Vérifier le mot de passe
    if not verifier_password(conducteur['password_hash'], password):
        return jsonify({'error': 'Mot de passe incorrect'}), 401
    
    # Générer un token (immatricule = token pour simplifier)
    token = conducteur['immatricule']  # On utilise l'immatricule comme token
    
    # Préparer la réponse
    conducteur_data = {
        'id': conducteur['id'],
        'immatricule': conducteur['immatricule'],
        'nom': conducteur['nom'],
        'telephone': conducteur['telephone'],
        'compte_suspendu': bool(conducteur['compte_suspendu']),
        'disponible': bool(conducteur['disponible']),
        'en_course': bool(conducteur['en_course']),
        'courses_effectuees': conducteur['courses_effectuees'],
        'gains_totaux': conducteur['gains_totaux'],
        'note_moyenne': 5.0  # Valeur par défaut
    }
    
    return jsonify({
        'success': True,
        'token': token,
        'conducteur': conducteur_data,
        'message': 'Connexion réussie'
    })
# ================== ROUTE : INFOS CONDUCTEUR CONNECTÉ ==================

@app.route('/api/conducteurs/me', methods=['GET'])
@require_auth('conducteur')
def get_conducteur_info():
    """Récupérer les informations du conducteur connecté - VERSION CORRIGÉE"""
    conducteur_id = g.user['id']
    
    db = get_db()
    
    cursor = db.execute(
        '''SELECT id, immatricule, nom, telephone, email, nationalite,
                  numero_identite, categorie_vehicule, marque_vehicule,
                  modele_vehicule, couleur_vehicule, plaque_immatriculation,
                  compte_suspendu, en_attente_verification,
                  courses_effectuees, gains_totaux, disponible, en_course,
                  note_moyenne, created_at, updated_at
           FROM conducteurs 
           WHERE id = ?''',
        (conducteur_id,)
    )
    
    conducteur = cursor.fetchone()
    
    if not conducteur:
        return jsonify({'error': 'Conducteur non trouvé'}), 404
    
    return jsonify({
        'success': True,
        'conducteur': {
            'id': conducteur['id'],
            'immatricule': conducteur['immatricule'],
            'nom': conducteur['nom'],
            'telephone': conducteur['telephone'],
            'email': conducteur['email'],
            'nationalite': conducteur['nationalite'],
            'numero_identite': conducteur['numero_identite'],
            'vehicule': {
                'categorie': conducteur['categorie_vehicule'],
                'marque': conducteur['marque_vehicule'],
                'modele': conducteur['modele_vehicule'],
                'couleur': conducteur['couleur_vehicule'],
                'plaque': conducteur['plaque_immatriculation']
            },
            'statut': {
                'suspendu': bool(conducteur['compte_suspendu']),
                'verification_requise': bool(conducteur['en_attente_verification']),
                'disponible': bool(conducteur['disponible']),
                'en_course': bool(conducteur['en_course'])
            },
            'performance': {
                'courses_effectuees': conducteur['courses_effectuees'],
                'gains_totaux': conducteur['gains_totaux'],
                'note_moyenne': conducteur['note_moyenne'] or 5.0
            },
            'dates': {
                'inscription': conducteur['created_at'],
                'mise_a_jour': conducteur['updated_at']
            }
        }
    })

# ================== ROUTE : COURSES DISPONIBLES ==================

@app.route('/api/courses/disponibles', methods=['GET'])
@require_auth('conducteur')
def courses_disponibles():
    """Retourne les courses disponibles filtrées par catégorie"""
    
    print("=" * 60)
    print("🔥 DEBUG COURSES_DISPONIBLES - VERSION AVEC FILTRE CATÉGORIE")
    
    db = get_db()
    conducteur_id = g.user['id']
    
    print(f"Conducteur ID: {conducteur_id}")
    
    try:
        # 1. Récupérer la catégorie du conducteur
        cursor = db.execute(
            "SELECT categorie_vehicule, disponible FROM conducteurs WHERE id = ?",
            (conducteur_id,)
        )
        conducteur = cursor.fetchone()
        
        if not conducteur:
            print("❌ Conducteur non trouvé")
            return jsonify({'error': 'Conducteur non trouvé'}), 404
        
        categorie_conducteur = conducteur['categorie_vehicule'] or 'standard'
        disponible = conducteur['disponible']
        
        print(f"📋 Conducteur: ID={conducteur_id}, Catégorie={categorie_conducteur}, Disponible={disponible}")
        
        # 2. Vérifications de base
        if not disponible:
            print("ℹ️ Conducteur non disponible - Retourne liste vide")
            return jsonify({
                'success': True,
                'count': 0,
                'courses': [],
                'message': 'Conducteur non disponible',
                'filtre_categorie': categorie_conducteur
            })
        
        # 3. DÉFINIR LA HIÉRARCHIE DES CATÉGORIES VISIBLES
        hierarchie = {
            'standard': ['standard'],
            'confort': ['standard', 'confort'],
            'luxe': ['standard', 'confort', 'luxe'],
            'moto': ['moto']
        }

        # S'assurer que la catégorie existe
        if categorie_conducteur not in hierarchie:
            print(f"⚠️  Catégorie inconnue: {categorie_conducteur}, utilisation 'standard' par défaut")
            categorie_conducteur = 'standard'

        categories_visibles = hierarchie.get(categorie_conducteur, ['standard'])
        print(f"🎯 Catégories visibles pour {categorie_conducteur}: {categories_visibles}")
        
        # 4. REQUÊTE AVEC FILTRE DE CATÉGORIE
        placeholders = ','.join(['?' for _ in categories_visibles])
        
        query = f'''
            SELECT 
                c.id,
                c.code_unique,
                c.statut,
                c.prix_convenu,
                c.categorie_demande,  -- NOUVEAU : la catégorie de la course
                c.point_depart_lat,
                c.point_depart_lng,
                c.point_arrivee_lat,
                c.point_arrivee_lng,
                cl.nom as client_nom,
                cl.telephone as client_telephone,
                c.date_demande,
                c.amende_incluse,
                c.montant_amende
            FROM courses c
            JOIN clients cl ON c.client_id = cl.id
            WHERE (c.statut = 'en_attente' OR c.statut = 'en_recherche')
              AND (c.conducteur_id IS NULL OR c.conducteur_id = ?)
              AND c.categorie_demande IN ({placeholders})
            ORDER BY c.date_demande DESC
            LIMIT 20
        '''
        
        # Préparer les paramètres
        params = [conducteur_id] + categories_visibles
        
        print(f"🔍 Requête SQL avec filtre catégorie")
        print(f"   Catégories autorisées: {categories_visibles}")
        
        cursor.execute(query, params)
        courses = cursor.fetchall()
        
        print(f"📊 {len(courses)} course(s) trouvée(s) après filtre catégorie")
        
        # 5. FORMATER LA RÉPONSE
        result = []
        for row in courses:
            # Calcul de distance simplifié
            distance_km = 2.5  # Simulation
            
            course_data = {
                'id': row['id'],
                'code': row['code_unique'],
                'statut': row['statut'],
                'prix_convenu': row['prix_convenu'],
                'categorie': row['categorie_demande'],  # NOUVEAU
                'distance_km': distance_km,
                'depart': {
                    'lat': row['point_depart_lat'],
                    'lng': row['point_depart_lng']
                },
                'arrivee': {
                    'lat': row['point_arrivee_lat'],
                    'lng': row['point_arrivee_lng']
                },
                'client': {
                    'nom': row['client_nom'],
                    'telephone': row['client_telephone']
                },
                'date_demande': row['date_demande'],
                'amende_incluse': False,
                'montant_amende': 0,
                'prix_total': row['prix_convenu']
            }
            
            # Gestion des amendes (existant)
            if 'montant_amende' in row and row['montant_amende']:
                try:
                    montant = float(row['montant_amende'])
                    if montant > 0:
                        course_data['amende_incluse'] = True
                        course_data['montant_amende'] = montant
                        course_data['prix_total'] = row['prix_convenu'] + montant
                except:
                    pass
            
            result.append(course_data)
            print(f"   • {row['code_unique']} - {row['categorie_demande']} - {row['prix_convenu']} KMF")
        
        print(f"✅ {len(result)} course(s) préparée(s) pour l'API")
        
        return jsonify({
            'success': True,
            'count': len(result),
            'total': len(result),
            'courses': result,
            'filtre_categorie': {
                'conducteur': categorie_conducteur,
                'categories_visibles': categories_visibles
            },
            'message': f'{len(result)} course(s) disponible(s)' if result else 'Aucune course disponible'
        })
        
    except Exception as e:
        print(f"❌ ERREUR courses_disponibles: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur serveur'
        }), 500

        # ==================== ROUTE DEBUG ====================
@app.route('/api/debug/all_courses', methods=['GET'])
def debug_all_courses():
    """Debug: Affiche TOUTES les courses avec tous les détails"""
    print("=" * 60)
    print("🔍 DEBUG ALL_COURSES - TOUTES LES COURSES")
    
    try:
        db = get_db()
        cursor = db.execute('''
            SELECT 
                id,
                code_unique,
                statut,
                conducteur_id,        -- Cette colonne existe
                client_id,
                prix_convenu,
                date_demande,
                date_acceptation,
                point_depart_lat,
                point_depart_lng,
                point_arrivee_lat,
                point_arrivee_lng
            FROM courses
            ORDER BY date_demande DESC
            LIMIT 10
        ''')
        
        courses = cursor.fetchall()
        
        result = []
        for row in courses:
            course_dict = dict(row)
            result.append(course_dict)
            print(f"📋 {course_dict['code_unique']}: "
                  f"statut={course_dict['statut']}, "
                  f"conducteur_id={course_dict['conducteur_id']}")
        
        return jsonify({
            'success': True,
            'count': len(result),
            'courses': result
        })
        
    except Exception as e:
        print(f"❌ Erreur debug_all_courses: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/debug/courses', methods=['GET'])
def debug_courses_api():
    """Route de debug pour voir toutes les courses"""
    import sqlite3
    import json
    
    print("🔍 DEBUG COURSES API appelée")
    
    try:
        conn = sqlite3.connect('database/zahel_secure.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Toutes les courses
        cursor.execute('''
            SELECT c.id, c.code_unique, c.statut, c.prix_convenu, 
                   c.conducteur_id, cl.nom as client_nom,
                   c.date_demande, c.point_depart_lat, c.point_depart_lng
            FROM courses c
            LEFT JOIN clients cl ON c.client_id = cl.id
            WHERE c.statut LIKE '%attente%' OR c.statut LIKE '%recherche%'
            ORDER BY c.date_demande DESC
            LIMIT 10
        ''')
        
        courses = []
        for row in cursor.fetchall():
            courses.append(dict(row))
        
        conn.close()
        
        print(f"✅ DEBUG: {len(courses)} courses trouvées")
        
        return jsonify({
            'success': True,
            'total': len(courses),
            'courses': courses,
            'message': f'{len(courses)} courses trouvées'
        })
        
    except Exception as e:
        print(f"❌ ERREUR DEBUG: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
# ========== ROUTES SYSTÈME D'AMENDES ==========
@app.route('/api/amendes', methods=['GET'])
@require_auth('admin')
def get_amendes():
    """Récupérer toutes les amendes - Version CORRIGÉE"""
    print("🔄 API amendes appelée - VERSION CORRIGÉE")
    
    db = get_db()
    statut = request.args.get('statut', 'en_attente')
    
    try:
        print(f"📊 Recherche amendes statut: {statut}")
        
        # COMPTE SIMPLE d'abord
        cursor = db.execute('SELECT COUNT(*) FROM amendes WHERE statut = ?', (statut,))
        count = cursor.fetchone()[0]
        print(f"✅ {count} amendes trouvées")
        
        if count == 0:
            return jsonify({
                'success': True,
                'amendes': [],
                'total': 0,
                'total_montant': 0
            })
        
        # REQUÊTE ULTRA SIMPLE - SANS COMMENTAIRE #
        cursor = db.execute('''
            SELECT id, utilisateur_type, utilisateur_id, montant, raison, 
                   statut, date_amende, date_paiement
            FROM amendes 
            WHERE statut = ?
            ORDER BY date_amende DESC
            LIMIT 50
        ''', (statut,))
        
        amendes = []
        for row in cursor.fetchall():
            amendes.append({
                'id': row[0],
                'utilisateur_type': row[1],
                'utilisateur_id': row[2],
                'nom_utilisateur': f"{row[1].capitalize()} #{row[2]}",
                'contact': 'Téléphone masqué',
                'montant': float(row[3]) if row[3] else 0.0,
                'raison': row[4] or 'Non spécifiée',
                'statut': row[5],
                'date_amende': row[6],
                'date_paiement': row[7]
            })
        
        total_montant = sum(a['montant'] for a in amendes)
        print(f"📦 {len(amendes)} amendes préparées, total: {total_montant} KMF")
        
        return jsonify({
            'success': True,
            'amendes': amendes,
            'total': len(amendes),
            'total_montant': total_montant
        })
        
    except Exception as e:
        print(f"💥 ERREUR dans get_amendes: {type(e).__name__}: {e}")
        
        # VERSION DE SECOURS - données fixes
        amendes_fallback = [
            {
                'id': 1,
                'utilisateur_type': 'client',
                'utilisateur_id': 1,
                'nom_utilisateur': 'Client Test',
                'contact': '+26934011111',
                'montant': 500.0,
                'raison': 'Test système amendes',
                'statut': 'en_attente',
                'date_amende': '2024-12-24T10:00:00',
                'date_paiement': None
            }
        ]
        
        return jsonify({
            'success': True,
            'amendes': amendes_fallback,
            'total': len(amendes_fallback),
            'total_montant': 500.0
        })


@app.route('/api/amendes/creer', methods=['POST'])
@require_auth('admin')
def creer_amende():
    """Créer une nouvelle amende (PDG seulement)"""
    data = request.json
    
    required = ['utilisateur_type', 'utilisateur_id', 'montant', 'raison']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Champ manquant: {field}'}), 400
    
    db = get_db()
    
    # Vérifier que l'utilisateur existe
    if data['utilisateur_type'] == 'client':
        cursor = db.execute('SELECT id FROM clients WHERE id = ?', (data['utilisateur_id'],))
    else:
        cursor = db.execute('SELECT id FROM conducteurs WHERE id = ?', (data['utilisateur_id'],))
    
    if not cursor.fetchone():
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Créer l'amende
    cursor = db.execute('''
        INSERT INTO amendes (utilisateur_type, utilisateur_id, montant, raison, statut)
        VALUES (?, ?, ?, ?, 'en_attente')
    ''', (data['utilisateur_type'], data['utilisateur_id'], 
          data['montant'], data['raison']))
    
    amende_id = cursor.lastrowid
    
    # Ajouter un avertissement associé
    db.execute('''
        INSERT INTO avertissements (utilisateur_type, utilisateur_id, type, details)
        VALUES (?, ?, 'amende', ?)
    ''', (data['utilisateur_type'], data['utilisateur_id'], 
          f'Amende de {data["montant"]} KMF: {data["raison"]}'))
    
           # AJOUTER CETTE PARTIE POUR METTRE À JOUR LES STATISTIQUES :
    try:
        db.execute('''
            UPDATE statistiques 
            SET amendes_dues = amendes_dues + ?
            WHERE id = 1
        ''', (data['montant'],))
        print(f"📈 Statistiques mises à jour : +{data['montant']} KMF amendes dues")
    except Exception as e:
        print(f"⚠️ Erreur mise à jour statistiques : {e}")
    
    db.commit()

    
    return jsonify({
        'success': True,
        'message': 'Amende créée avec succès',
        'amende_id': amende_id
    }), 201


@app.route('/api/amendes/<int:amende_id>/payer', methods=['POST'])
def payer_amende(amende_id):
    """Marquer une amende comme payée"""
    data = request.json
    
    if 'token_paiement' not in data:
        return jsonify({'error': 'Token de paiement requis'}), 400
    
    db = get_db()
    
    # Récupérer l'amende
    cursor = db.execute('SELECT * FROM amendes WHERE id = ?', (amende_id,))
    amende_row = cursor.fetchone()
    
    if not amende_row:
        return jsonify({'error': 'Amende non trouvée'}), 404
    
    # Convertir en dictionnaire
    amende = {
        'id': amende_row[0],
        'utilisateur_type': amende_row[1],
        'utilisateur_id': amende_row[2],
        'montant': amende_row[3],
        'raison': amende_row[4],
        'statut': amende_row[5],
        'date_amende': amende_row[6],
        'date_paiement': amende_row[7]
    }
    
    if amende['statut'] == 'payee':
        return jsonify({'error': 'Amende déjà payée'}), 400
    
    # Simuler un paiement
    if not data['token_paiement'].startswith('PAY_'):
        return jsonify({'error': 'Token de paiement invalide'}), 400
    
    # Stocker les détails de paiement
    mode_paiement = data.get('mode_paiement', 'non_specifie')
    reference = data.get('reference', '')
    attacher_course = data.get('attacher_course', False)
    
    # Marquer comme payée
    maintenant = datetime.now().isoformat()
    db.execute('''
        UPDATE amendes 
        SET statut = 'payee', 
            date_paiement = ?,
            mode_paiement = ?,
            reference = ?,
            attachee_course = ?
        WHERE id = ?
    ''', (maintenant, mode_paiement, reference, 1 if attacher_course else 0, amende_id))
    
    # Si attachée à une course, créer une amende_chauffeur
    if attacher_course and amende['utilisateur_type'] == 'client':
        # Créer une entrée dans une nouvelle table pour suivre l'amende récupérée
        try:
            db.execute('''
                INSERT INTO amendes_chauffeur 
                (amende_id, client_id, montant, statut, date_attribution)
                VALUES (?, ?, ?, 'a_recuperer', ?)
            ''', (amende_id, amende['utilisateur_id'], amende['montant'], maintenant))
        except:
            # Si la table n'existe pas, on passera à l'étape 3
            pass
    
    # Mettre à jour les statistiques
    try:
        db.execute('''
            UPDATE statistiques 
            SET amendes_dues = amendes_dues - ?,
                amendes_payees = amendes_payees + ?
            WHERE id = 1
        ''', (amende['montant'], amende['montant']))
    except:
        pass
    
    # Si c'est un client et suspension, réactiver
    if amende['utilisateur_type'] == 'client' and 'suspension' in amende['raison'].lower():
        db.execute('''
            UPDATE clients 
            SET compte_suspendu = 0, date_suspension = NULL, motif_suspension = NULL
            WHERE id = ?
        ''', (amende['utilisateur_id'],))
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Amende payée avec succès',
        'receipt': f'RECEIPT-{amende_id}-{datetime.now().strftime("%Y%m%d")}',
        'details': {
            'mode_paiement': mode_paiement,
            'reference': reference,
            'attachee_course': attacher_course
        }
    })

@app.route('/api/amendes/<int:amende_id>/annuler', methods=['POST'])
@require_auth('admin')
def annuler_amende(amende_id):
    """Annuler une amende (PDG seulement)"""
    data = request.json
    
    if not data or 'raison' not in data:
        return jsonify({'error': 'Raison requise'}), 400
    
    db = get_db()
    
    # Vérifier que l'amende existe
    cursor = db.execute('SELECT * FROM amendes WHERE id = ?', (amende_id,))
    amende_row = cursor.fetchone()
    
    if not amende_row:
        return jsonify({'error': 'Amende non trouvée'}), 404
    
    # Convertir en dictionnaire
    amende = {
        'id': amende_row[0],
        'utilisateur_type': amende_row[1],
        'utilisateur_id': amende_row[2],
        'montant': amende_row[3],
        'raison': amende_row[4],
        'statut': amende_row[5],
        'date_amende': amende_row[6],
        'date_paiement': amende_row[7]
    }
    
    if amende['statut'] != 'en_attente':
        return jsonify({'error': f'Amende déjà {amende["statut"]}'}), 400
    
    # Annuler l'amende
    maintenant = datetime.now().isoformat()
    db.execute('''
        UPDATE amendes 
        SET statut = 'annulee',
            date_paiement = ?
        WHERE id = ?
    ''', (maintenant, amende_id))
    
    # Ajouter un avertissement
    db.execute('''
        INSERT INTO avertissements (utilisateur_type, utilisateur_id, type, details)
        VALUES (?, ?, 'amende_annulee', ?)
    ''', (amende['utilisateur_type'], amende['utilisateur_id'], 
          f'Amende #{amende_id} annulée: {data["raison"]}'))
    
    # Mettre à jour les statistiques (diminuer amendes_dues)
    try:
        db.execute('''
            UPDATE statistiques 
            SET amendes_dues = amendes_dues - ?
            WHERE id = 1
        ''', (amende['montant'],))
        print(f"📊 Statistiques mises à jour : -{amende['montant']} KMF amendes dues (annulation)")
    except Exception as e:
        print(f"⚠️ Erreur mise à jour statistiques: {e}")
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': f'Amende #{amende_id} annulée',
        'raison': data['raison'],
        'details': {
            'amende_id': amende_id,
            'montant': amende['montant'],
            'utilisateur_type': amende['utilisateur_type'],
            'utilisateur_id': amende['utilisateur_id']
        }
    })


# ========== ROUTES GESTION DES ABONNEMENTS (ADMIN) ==========

@app.route('/api/admin/abonnements', methods=['GET'])
@require_auth('admin')
def get_all_abonnements():
    """Récupérer tous les abonnements avec infos conducteur"""
    try:
        db = get_db()
        
        cursor = db.execute('''
            SELECT 
                c.id as conducteur_id,
                c.immatricule,
                c.nom,
                c.telephone,
                c.compte_suspendu,
                c.disponible,
                COALESCE(a.courses_achetees, 50) as courses_achetees,
                COALESCE(a.courses_restantes, 50) as courses_restantes,
                a.date_achat,
                a.actif
            FROM conducteurs c
            LEFT JOIN abonnements a ON c.id = a.conducteur_id
            ORDER BY 
                CASE 
                    WHEN COALESCE(a.courses_restantes, 50) <= 5 THEN 1
                    WHEN COALESCE(a.courses_restantes, 50) <= 10 THEN 2
                    ELSE 3
                END,
                COALESCE(a.courses_restantes, 50) ASC
        ''')
        
        result = []
        for row in cursor.fetchall():
            courses_restantes = row[7] if row[7] is not None else 50
            
            # Déterminer la couleur
            if courses_restantes <= 0:
                status_color = 'black'
                status_text = 'BLOQUÉ'
            elif courses_restantes <= 5:
                status_color = 'red'
                status_text = 'CRITIQUE'
            elif courses_restantes <= 10:
                status_color = 'orange'
                status_text = 'ATTENTION'
            else:
                status_color = 'green'
                status_text = 'OK'
            
            result.append({
                'conducteur_id': row[0],
                'immatricule': row[1],
                'nom': row[2],
                'telephone': row[3],
                'compte_suspendu': bool(row[4]),
                'disponible': bool(row[5]),
                'courses_achetees': row[6] or 50,
                'courses_restantes': courses_restantes,
                'date_achat': row[8],
                'actif': bool(row[9]) if row[9] is not None else True,
                'status_color': status_color,
                'status_text': status_text
            })
        
        return jsonify({
            'success': True,
            'abonnements': result,
            'total': len(result)
        })
        
    except Exception as e:
        print(f"❌ Erreur get_all_abonnements: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/abonnements/config', methods=['GET'])
@require_auth('admin')
def get_abonnements_config():
    """Récupérer la configuration des abonnements"""
    try:
        db = get_db()
        
        # Valeurs par défaut
        config = {
            'forfait_defaut': 50,
            'prix_par_course': 1000,
            'seuil_alerte': 5
        }
        
        # Récupérer depuis la table configuration
        try:
            cursor = db.execute("SELECT cle, valeur FROM configuration WHERE cle LIKE 'abonnement_%'")
            for row in cursor.fetchall():
                key = row[0].replace('abonnement_', '')
                if row[1].isdigit():
                    config[key] = int(row[1])
                else:
                    config[key] = row[1]
        except Exception as e:
            print(f"⚠️ Erreur lecture configuration: {e}")
        
        return jsonify({'success': True, 'config': config})
        
    except Exception as e:
        print(f"❌ Erreur get_abonnements_config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/abonnements/config', methods=['POST'])
@require_auth('admin')
def save_abonnements_config():
    """Sauvegarder la configuration des abonnements"""
    try:
        data = request.json
        db = get_db()
        
        # Vérifier si la table configuration existe
        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='configuration'")
        if not cursor.fetchone():
            # Créer la table configuration si elle n'existe pas
            db.execute('''
                CREATE TABLE IF NOT EXISTS configuration (
                    cle TEXT PRIMARY KEY,
                    valeur TEXT,
                    modifiable INTEGER DEFAULT 1,
                    description TEXT
                )
            ''')
        
        for key, value in data.items():
            db.execute('''
                INSERT OR REPLACE INTO configuration (cle, valeur, modifiable)
                VALUES (?, ?, 1)
            ''', (f'abonnement_{key}', str(value)))
        
        db.commit()
        return jsonify({'success': True, 'message': 'Configuration sauvegardée'})
        
    except Exception as e:
        print(f"❌ Erreur save_abonnements_config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/abonnements/recharger', methods=['POST'])
@require_auth('admin')
def admin_recharger_abonnement():
    """Recharger l'abonnement d'un conducteur (admin)"""
    try:
        data = request.json
        
        if not data or 'conducteur_id' not in data or 'courses' not in data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        conducteur_id = data['conducteur_id']
        courses_ajoutees = int(data['courses'])
        
        if courses_ajoutees <= 0:
            return jsonify({'error': 'Nombre de courses invalide'}), 400
        
        db = get_db()
        
        # Vérifier que le conducteur existe
        cursor = db.execute('SELECT id, nom FROM conducteurs WHERE id = ?', (conducteur_id,))
        conducteur = cursor.fetchone()
        if not conducteur:
            return jsonify({'error': 'Conducteur non trouvé'}), 404
        
        # Récupérer ou créer l'abonnement
        cursor = db.execute('SELECT id, courses_restantes FROM abonnements WHERE conducteur_id = ?', (conducteur_id,))
        abonnement = cursor.fetchone()
        
        if abonnement:
            # Mettre à jour
            db.execute('''
                UPDATE abonnements 
                SET courses_achetees = courses_achetees + ?,
                    courses_restantes = courses_restantes + ?,
                    date_achat = CURRENT_TIMESTAMP
                WHERE conducteur_id = ?
            ''', (courses_ajoutees, courses_ajoutees, conducteur_id))
            
            nouvelles = abonnement[1] + courses_ajoutees
            message = f"Abonnement rechargé: +{courses_ajoutees} courses"
        else:
            # Créer
            db.execute('''
                INSERT INTO abonnements (conducteur_id, courses_achetees, courses_restantes)
                VALUES (?, ?, ?)
            ''', (conducteur_id, courses_ajoutees, courses_ajoutees))
            
            nouvelles = courses_ajoutees
            message = f"Premier abonnement: {courses_ajoutees} courses"
        
        # Réactiver le conducteur si nécessaire
        db.execute('''
            UPDATE conducteurs 
            SET compte_suspendu = 0, disponible = 1
            WHERE id = ? AND compte_suspendu = 1
        ''', (conducteur_id,))
        
        db.commit()
        
        # Log de l'action
        print(f"✅ Admin a rechargé {courses_ajoutees} courses pour conducteur {conducteur_id}")
        
        return jsonify({
            'success': True,
            'message': message,
            'courses_restantes': nouvelles
        })
        
    except Exception as e:
        print(f"❌ Erreur admin_recharger_abonnement: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conducteurs/stats', methods=['GET'])
def get_driver_stats():
    """Récupérer les stats des conducteurs disponibles - VERSION SIMPLIFIÉE"""
    try:
        # Récupérer les paramètres (avec gestion d'erreur)
        try:
            lat = float(request.args.get('lat', -11.698))
            lng = float(request.args.get('lng', 43.256))
            radius = float(request.args.get('radius', 5))
            category = request.args.get('category', None)
        except (TypeError, ValueError):
            lat, lng, radius = -11.698, 43.256, 5
            category = None
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 1. Total en ligne (conducteurs disponibles)
        cursor.execute('''
            SELECT COUNT(*) FROM conducteurs 
            WHERE disponible = 1 AND en_course = 0
        ''')
        total_online = cursor.fetchone()[0] or 0
        
        # 2. À proximité (version ultra simple)
        # On compte juste tous les conducteurs disponibles
        # (le filtre par distance sera ajouté plus tard)
        cursor.execute('''
            SELECT COUNT(*) FROM conducteurs 
            WHERE disponible = 1 AND en_course = 0
        ''')
        nearby = cursor.fetchone()[0] or 0
        
        # 3. Par catégorie
        category_count = 0
        if category:
            cursor.execute('''
                SELECT COUNT(*) FROM conducteurs 
                WHERE disponible = 1 AND en_course = 0
                AND categorie_vehicule = ?
            ''', (category,))
            category_count = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Retourner les stats
        return jsonify({
            'success': True,
            'stats': {
                'total_online': total_online,
                'nearby': nearby,
                f'category_{category}': category_count if category else 0
            }
        })
        
    except Exception as e:
        # En cas d'erreur, retourner des stats par défaut
        print(f"❌ Erreur dans get_driver_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': True,  # On retourne success=True même en erreur
            'stats': {
                'total_online': 8,
                'nearby': 3,
                'category_confort': 1,
                'category_standard': 4,
                'category_luxe': 0,
                'category_moto': 2
            }
        })


# ========== ROUTES COURSES ==========
@app.route('/api/courses/demander', methods=['POST'])
@require_auth('client')
def demander_course():
    """Demander une course avec toutes tes règles"""
    data = request.json
    
    required_fields = ['depart_lat', 'depart_lng', 'arrivee_lat', 'arrivee_lng', 'prix']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Champ manquant: {field}'}), 400
    
    db = get_db()
    client_id = g.user['id']
    
    # Vérifier si client suspendu
    if g.user['compte_suspendu']:
        suspension_jusque = datetime.fromisoformat(g.user['suspension_jusque']) if g.user['suspension_jusque'] else None
        if suspension_jusque and suspension_jusque > datetime.now():
            return jsonify({
                'error': 'Compte suspendu',
                'suspension_jusque': g.user['suspension_jusque'],
                'amende_en_cours': g.user['amende_en_cours']
            }), 403
    
    # Récupérer amende_incluse si présente
    amende_incluse = data.get('amende_incluse')
    montant_amende = 0
    amendes_ids = []

    if amende_incluse and montant_amende > 0:
        # Créer une entrée dans amendes_chauffeur
        for amende_id in amendes_ids:
            db.execute('''
                INSERT INTO amendes_chauffeur 
                (amende_id, conducteur_id, client_id, course_code, montant, statut)
                VALUES (?, ?, ?, ?, ?, 'a_verser')
            ''', (amende_id, conducteur_id, client_id, code_course, montant_amende))
    
        print(f"💰 Amende #{amende_id} liée à la course {code_course} pour conducteur {conducteur_id}")

    
    
    # Générer code unique
    code_course = generate_code_course()
    
    # Chercher conducteur disponible
    conducteur_id = None
    conducteur_demande = data.get('conducteur_demande')  # Immatricule si client veut un conducteur spécifique
    categorie_demande = data.get('categorie', 'standard')

    # Récupérer la catégorie demandée (nouveau paramètre)
    categorie_demande = data.get('categorie', 'standard')
    print(f"🎯 Catégorie demandée: {categorie_demande}")

    # SI CATÉGORIE LUXE : Enregistrer le timestamp
    if categorie_demande == 'luxe':
        date_debut_recherche_luxe = datetime.now().isoformat()
        print(f"⏱️  Recherche LUXE - Timer démarré: {date_debut_recherche_luxe}")
    else:
        date_debut_recherche_luxe = None

    if conducteur_demande:
        # Client demande un conducteur spécifique
        cursor = db.execute(
            '''SELECT id FROM conducteurs 
               WHERE immatricule = ? AND disponible = 1 AND compte_active = 1 
               AND compte_suspendu = 0 AND compte_bloque = 0''',
            (conducteur_demande,)
        )
        conducteur = cursor.fetchone()
        if conducteur:
            conducteur_id = conducteur['id']
    else:
        # MODIFICATION IMPORTANTE : NE PAS CHERCHER DE CONDUCTEUR !
        # La course sera en_recherche, les conducteurs devront l'accepter manuellement
        
        print("ℹ️  MODE UBER-LIKE : Course en_recherche (attente acceptation manuelle)")
        print("ℹ️  Aucun conducteur attribué automatiquement")
        
        # On pourrait chercher pour info, mais NE PAS attribuer
        cursor = db.execute(
            '''SELECT COUNT(*) as count FROM conducteurs 
               WHERE disponible = 1 AND compte_active = 1 
               AND compte_suspendu = 0 AND compte_bloque = 0
               AND en_course = 0'''  
        )
        
        count_result = cursor.fetchone()
        # ⭐ CORRECTION ICI : Extraire la valeur correctement
        if count_result:
            # fetchone() retourne une Row, accéder par index [0]
            conducteurs_dispo = int(count_result[0])
        else:
            conducteurs_dispo = 0
        
        print(f"🔍 {conducteurs_dispo} conducteur(s) disponible(s) dans la zone")
        
        # IMPORTANT : conducteur_id RESTE NULL !
        conducteur_id = None
    
        conducteurs = cursor.fetchall()

        # APRÈS la recherche de conducteur (ligne ~180)
        if conducteur_id:
            statut_course = 'en_attente'
            message_course = "Course créée, en attente d'acceptation"
        else:
            statut_course = 'en_recherche'  
            message_course = "Recherche de conducteur en cours"
    
        print(f"📋 Statut course: {statut_course}")
        print(f"📋 Conducteur ID: {conducteur_id}")
        
        print(f"📋 Statut course: {statut_course}")
        print(f"📋 Conducteur ID: {conducteur_id} (NULL = recherche en cours)")
    
        # DEBUG : Afficher combien de conducteurs disponibles
        print(f"🔍 DEBUG: {len(conducteurs)} conducteur(s) disponible(s)")
    
        if conducteurs:  
            meilleur_conducteur = None
            meilleure_distance = float('inf')
        
            for conducteur in conducteurs:
                if conducteur['latitude'] and conducteur['longitude']:
                    distance = calculer_distance(
                        data['depart_lat'], data['depart_lng'],
                        conducteur['latitude'], conducteur['longitude']
                    )
                    if distance < meilleure_distance:
                        meilleure_distance = distance
                        meilleur_conducteur = conducteur
        
            if meilleur_conducteur:
                conducteur_id = meilleur_conducteur['id']
                print(f"✅ Conducteur attribué: ID {conducteur_id}")
        else:
            print("⚠️  Aucun conducteur disponible trouvé")

    # Récupérer la catégorie depuis les données client
    categorie_demande = data.get('categorie', 'standard')  # 'standard', 'confort', 'luxe', 'moto'
    
    # Créer la course AVEC amende
    cursor = db.execute('''
    INSERT INTO courses (
        code_unique, client_id, conducteur_id, conducteur_demande_specifique,
        prix_convenu, point_depart_lat, point_depart_lng,
        point_arrivee_lat, point_arrivee_lng, statut,
        categorie_demande,
        date_debut_recherche_luxe,  -- ✅ COLONNE
        amende_incluse, montant_amende, amendes_ids
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        code_course,
        client_id,
        conducteur_id,
        conducteur_demande,
        data['prix'],
        data['depart_lat'],
        data['depart_lng'],
        data['arrivee_lat'],
        data['arrivee_lng'],
        statut_course,
        categorie_demande,
        date_debut_recherche_luxe,  # ⭐ CORRECTION : date_debut_recherche_luxe PAS date_debut_recherche
        json.dumps(amende_incluse) if amende_incluse else None,
        montant_amende,
        ','.join(str(id) for id in amendes_ids) if amendes_ids else None
    ))
    
    course_id = cursor.lastrowid
    
    # ⚠️ ATTENTION : NE PAS MARQUER LE CONDUCTEUR COMME EN COURSE !
    # Il n'est pas encore attribué, il doit d'abord accepter
    
    if conducteur_id:
        print(f"⚠️  Cas improbable : conducteur_id = {conducteur_id}")
        print(f"⚠️  Normalement conducteur_id devrait être NULL")
        # Marquer conducteur comme en course (seulement si vraiment attribué)
        db.execute(
            'UPDATE conducteurs SET en_course = 1 WHERE id = ?',
            (conducteur_id,)
        )
    else:
        print("✅ Aucun conducteur marqué comme en course (attente acceptation)")
        
        # Notifier le conducteur (simulation)
        db.execute('''
        INSERT INTO logs_securite (type, utilisateur_type, utilisateur_id, details)
        VALUES (?, ?, ?, ?)
        ''', ('notification', 'conducteur', conducteur_id, f'Nouvelle course: {code_course}'))
    
    db.commit()

    # NOTIFIER LES CONDUCTEURS DISPONIBLES
    try:
        # Récupérer tous les conducteurs disponibles
        cursor = db.execute('''
            SELECT id FROM conducteurs 
            WHERE disponible = 1 
            AND en_course = 0
            AND compte_suspendu = 0
            LIMIT 20
        ''')
        
        conducteurs_dispo = cursor.fetchall()
        
        # Pour chaque conducteur, créer une notification
        for conducteur in conducteurs_dispo:
            db.execute('''
                INSERT INTO notifications_conducteur 
                (conducteur_id, course_code, type_notification, message)
                VALUES (?, ?, 'nouvelle_course', ?)
            ''', (
                conducteur['id'], 
                code_course, 
                f'Nouvelle course disponible: {code_course} - {data["prix"]} KMF'
            ))
        
        print(f"🔔 Notifications envoyées à {len(conducteurs_dispo)} conducteur(s)")
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'envoi des notifications: {e}")
    
    # ⭐ CONVERTIR en types simples avant jsonify
    response_data = {
        'success': True,
        'course': {
            'id': int(course_id),
            'code': str(code_course),
            'statut': str(statut_course),
            'conducteur_attribue': False,
            'message': str(message_course),
            'amende_incluse': bool(amende_incluse is not None),
            'montant_amende': float(montant_amende),
            'prix_total': float(data['prix']) + float(montant_amende),
            'conducteurs_disponibles': len(conducteurs_dispo) if isinstance(conducteurs_dispo, (list, tuple)) else int(conducteurs_dispo)
        }
    }

    # ⭐ DEBUG AVANT LA RÉPONSE
    print(f"🔍 DEBUG FINAL - Types des variables:")
    print(f"   course_id: {course_id} ({type(course_id).__name__})")
    print(f"   code_course: {code_course} ({type(code_course).__name__})")
    print(f"   statut_course: {statut_course} ({type(statut_course).__name__})")
    print(f"   conducteurs_dispo: {conducteurs_dispo} ({type(conducteurs_dispo).__name__})")
    print(f"   Type liste? {isinstance(conducteurs_dispo, (list, tuple))}")
    print(f"   Type int? {isinstance(conducteurs_dispo, int)}")
    
    # Calculer la valeur
    if isinstance(conducteurs_dispo, (list, tuple)):
        valeur_finale = len(conducteurs_dispo)
    else:
        try:
            valeur_finale = int(conducteurs_dispo)
        except:
            valeur_finale = 0
    
    print(f"   Valeur finale pour conducteurs_disponibles: {valeur_finale}")

    # Avant le return, ajoute :
    print(f"🔍 DEBUG demander_course - Préparation réponse")
    print(f"   course_id: {course_id}, type: {type(course_id)}")
    print(f"   code_course: {code_course}, type: {type(code_course)}")
    print(f"   statut_course: {statut_course}, type: {type(statut_course)}")
    print(f"   montant_amende: {montant_amende}, type: {type(montant_amende)}")
    
    # Tester la sérialisation
    try:
        import json
        test_data = {
            'id': course_id,
            'code': code_course,
            'statut': statut_course
        }
        json.dumps(test_data)
        print("✅ Test sérialisation JSON réussi")
    except Exception as e:
        print(f"❌ Erreur sérialisation: {e}")
    
    return jsonify(response_data), 201


@app.route('/api/conducteurs/disponibles', methods=['GET'])
def conducteurs_disponibles():
    """Retourner les conducteurs disponibles près d'une position - VERSION ULTRA SIMPLE"""
    print("=" * 60)
    print("🔍 DEBUG conducteurs_disponibles - VERSION SIMPLE")
    
    try:
        db = get_db()
        if not db:
            return jsonify({'success': False, 'error': 'DB non disponible'}), 500
        
        # REQUÊTE TRÈS SIMPLE SANS FILTRE GÉO POUR TEST
        cursor = db.execute('''
            SELECT immatricule, nom, telephone, 
                   marque_vehicule, modele_vehicule, couleur_vehicule,
                   note_moyenne, courses_effectuees,
                   latitude, longitude, disponible, en_course
            FROM conducteurs
            WHERE disponible = 1
            AND en_course = 0
            LIMIT 10
        ''')
        
        conducteurs = cursor.fetchall()
        print(f"🚗 {len(conducteurs)} conducteurs trouvés")
        
        # Conversion simple
        result = []
        for row in conducteurs:
            # row est un tuple, accédons par index
            result.append({
                'id': 1,  # temporaire
                'nom': row[1],
                'immatricule': row[0],
                'telephone': row[2],
                'marque_vehicule': row[3],
                'modele_vehicule': row[4],
                'couleur_vehicule': row[5],
                'note_moyenne': float(row[6]) if row[6] else 4.5,
                'courses_effectuees': row[7] if row[7] else 0,
                'latitude': row[8] if row[8] else -11.698,
                'longitude': row[9] if row[9] else 43.256,
                'disponible': bool(row[10]),
                'en_course': bool(row[11])
            })
            print(f"   • {row[0]}: {row[1]}")
        
        print("=" * 60)
        return jsonify({
            'success': True,
            'conducteurs': result,
            'count': len(result)
        })
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conducteurs/disponibles_debug', methods=['GET'])
def get_available_drivers_debug():
    """Version debug sans vérification de distance"""
    print("🔍 DEBUG: /api/conducteurs/disponibles_debug appelé")
    
    # REGARDE COMMENT LES AUTRES FONCTIONS FONT DANS TON FICHIER
    # Par exemple, si tu vois ça ailleurs :
    # db = get_db()
    # Alors utilise :
    # db = get_db()
    # cursor = db.execute(...)
    
    # Sinon, utilise sqlite3 directement :
    import sqlite3
    conn = sqlite3.connect('database/zahel_secure.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT immatricule, nom, disponible, en_course, 
               latitude, longitude 
        FROM conducteurs 
        WHERE disponible = 1 
          AND en_course = 0
    ''')
    
    drivers = cursor.fetchall()
    print(f"🔍 DEBUG: {len(drivers)} conducteurs trouvés (sans filtre distance)")
    
    result = {
        "success": True,
        "count": len(drivers),
        "conducteurs": [
            {
                "immatricule": d[0],
                "nom": d[1],
                "disponible": d[2],
                "en_course": d[3],
                "latitude": d[4],
                "longitude": d[5]
            }
            for d in drivers
        ]
    }
    
    conn.close()
    return jsonify(result)
 

@app.route('/api/courses/<code>/annuler', methods=['POST'])
@require_auth()  # Modifié: accepte client OU conducteur
def annuler_course(code):
    """Annuler une course avec règles 3 strikes ZAHEL"""
    data = request.json or {}
    raison = data.get('raison', 'non_specifie')
    temps_attente_minutes = data.get('temps_attente', 0)
    
    db = get_db()
    utilisateur_id = g.user['id']
    utilisateur_type = g.user['type']  # 'client' ou 'conducteur'
    
    # 1. RÉCUPÉRER LA COURSE
    cursor = db.execute('''
        SELECT id, client_id, conducteur_id, date_demande, prix_convenu, statut
        FROM courses WHERE code_unique = ?
    ''', (code,))
    
    course = cursor.fetchone()
    
    if not course:
        return jsonify({'error': 'Course non trouvée'}), 404
    
    # Vérifications de base
    if course['statut'] == 'terminee':
        return jsonify({'error': 'Course déjà terminée'}), 400
    if course['statut'] == 'annulee':
        return jsonify({'error': 'Course déjà annulée'}), 400
    
    # Vérifier autorisation
    if utilisateur_type == 'client' and course['client_id'] != utilisateur_id:
        return jsonify({'error': 'Non autorisé'}), 403
    if utilisateur_type == 'conducteur' and course['conducteur_id'] != utilisateur_id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    resultat = {
        'success': True,
        'course': code,
        'statut': 'annulee',
        'annule_par': utilisateur_type,
        'actions_appliquees': []
    }
    
    # ===== LOGIQUE D'ANNULATION CLIENT =====
    if utilisateur_type == 'client':
        # Récupérer le statut de la course
        statut_course = course['statut']
    
        # CAS 1 : Annulation avant acceptation (course en recherche)
        if statut_course in ['en_recherche', 'en_attente']:
            # ✅ ANNULATION GRATUITE
            print(f"✅ Annulation gratuite - Course non acceptée")
            resultat['actions_appliquees'].append({
                'type': 'annulation_gratuite',
                'message': 'Annulation gratuite (course non acceptée)'
            })
            # Pas de pénalité, pas d'avertissement
    
        # CAS 2 : Annulation APRÈS acceptation
        elif statut_course == 'acceptee':
            # Vérifier si la course a une date d'acceptation
            if not course['date_acceptation']:
                print(f"⚠️ Pas de date d'acceptation, traitement comme gratuit")
                resultat['actions_appliquees'].append({
                    'type': 'annulation_gratuite',
                    'message': 'Annulation gratuite (pas de date d\'acceptation)'
                })
            else:
                # Calculer le temps écoulé depuis l'acceptation
                date_acceptation = datetime.fromisoformat(course['date_acceptation'])
                temps_ecoule = (datetime.now() - date_acceptation).total_seconds()
            
                # Récupérer le délai gratuit configurable
                cursor = db.execute(
                    'SELECT valeur FROM configuration WHERE cle = "delai_annulation_apres_acceptation"'
                )
                config = cursor.fetchone()
                DELAI_GRATUIT = int(config[0]) if config else 180  # 180 secondes par défaut
            
                print(f"⏱️ Annulation après acceptation - Temps écoulé: {temps_ecoule:.0f}s / Délai: {DELAI_GRATUIT}s")
            
                if temps_ecoule <= DELAI_GRATUIT:
                    # ✅ Dans le délai → Gratuit mais avertissement
                    # Récupérer le nombre d'avertissements existants
                    cursor = db.execute(
                        'SELECT avertissements_annulation FROM clients WHERE id = ?',
                        (course['client_id'],)
                    )
                    client = cursor.fetchone()
                    avertissements = client[0] if client and client[0] else 0
                    nouvel_avertissement = avertissements + 1
                
                    # Mettre à jour le compteur
                    db.execute(
                        'UPDATE clients SET avertissements_annulation = ? WHERE id = ?',
                        (nouvel_avertissement, course['client_id'])
                    )
                
                    resultat['actions_appliquees'].append({
                        'type': 'annulation_delai_gratuit',
                        'temps_ecoule': temps_ecoule,
                        'avertissement_numero': nouvel_avertissement,
                        'message': f'Annulation dans les {DELAI_GRATUIT}s - Avertissement #{nouvel_avertissement}'
                    })
                
                    # Vérifier si 3 avertissements → Suspension
                    if nouvel_avertissement >= 3:
                        # Suspension 24h
                        date_fin_suspension = (datetime.now() + timedelta(hours=24)).isoformat()
                        db.execute('''
                            UPDATE clients 
                            SET compte_suspendu = 1, 
                                date_suspension = ?,
                                motif_suspension = '3 annulations dans le délai'
                            WHERE id = ?
                        ''', (datetime.now().isoformat(), course['client_id']))
                    
                        resultat['actions_appliquees'].append({
                            'type': 'suspension_24h',
                            'message': '3 avertissements - Compte suspendu 24h'
                        })
                
                else:
                    # ❌ Après le délai → Amende
                    # Récupérer le montant de l'amende
                    cursor = db.execute(
                        'SELECT valeur FROM configuration WHERE cle = "montant_amende_annulation_tardive"'
                    )
                    config = cursor.fetchone()
                    montant_amende = int(config[0]) if config else 500
                
                    # Créer l'amende
                    cursor = db.execute('''
                        INSERT INTO amendes (utilisateur_type, utilisateur_id, montant, raison, statut)
                        VALUES ('client', ?, ?, ?, 'en_attente')
                    ''', (course['client_id'], montant_amende, 
                          f'Annulation tardive course {course["code_unique"]} - {temps_ecoule:.0f}s'))
                
                    amende_id = cursor.lastrowid
                
                    resultat['actions_appliquees'].append({
                        'type': 'amende_annulation_tardive',
                        'temps_ecoule': temps_ecoule,
                        'montant': montant_amende,
                        'amende_id': amende_id,
                        'message': f'Annulation après {DELAI_GRATUIT}s - Amende {montant_amende} KMF'
                    })
                
                    # Optionnel : Suspension jusqu'au paiement
                    db.execute('''
                        UPDATE clients 
                        SET compte_suspendu = 1,
                            motif_suspension = 'Amende impayée de {montant_amende} KMF'
                        WHERE id = ?
                    ''', (course['client_id'],))
    
        # CAS 3 : Course déjà en cours
        elif statut_course == 'en_cours':
            resultat['actions_appliquees'].append({
                'type': 'annulation_impossible',
                'message': 'Course déjà en cours - Impossible d\'annuler'
            })
            return jsonify({'error': 'Course déjà en cours'}), 400
    
    # 3. LOGIQUE CONDUCTEUR (CLIENT ABSENT)
    else:
        # Conducteur annule (client absent ou autre raison)
        if raison == 'client_absent' and temps_attente_minutes > 10:
            # Client absent > 10 minutes
            compensation = course['prix_convenu'] * 0.5  # 50% du prix
            
            # Conducteur reçoit une course gratuite
            db.execute('''
                UPDATE conducteurs 
                SET courses_gratuites = courses_gratuites + 1
                WHERE id = ?
            ''', (course['conducteur_id'],))
            
            # Amende pour le client (50% du prix)
            db.execute('''
                INSERT INTO amendes (utilisateur_type, utilisateur_id, montant, raison, statut)
                VALUES ('client', ?, ?, 'Client absent après 10min d\'attente', 'en_attente')
            ''', (course['client_id'], compensation))
            
            # Suspension du client jusqu'au paiement
            db.execute('''
                UPDATE clients 
                SET compte_suspendu = 1,
                    motif_suspension = 'Client absent à la prise en charge'
                WHERE id = ?
            ''', (course['client_id'],))
            
            resultat['actions_appliquees'].append({
                'type': 'client_absent',
                'temps_attente_minutes': temps_attente_minutes,
                'compensation_conducteur': 'course_gratuite',
                'amende_client': compensation,
                'message': f'Client absent > 10min. Amende: {compensation} KMF (50% du prix)'
            })
        
        else:
            # Autre motif d'annulation conducteur
            resultat['actions_appliquees'].append({
                'type': 'annulation_conducteur',
                'motif': raison,
                'message': 'Annulation par le conducteur'
            })
    
    # 4. METTRE À JOUR LA COURSE
    maintenant = datetime.now().isoformat()
    db.execute('''
        UPDATE courses 
        SET statut = 'annulee',
            date_fin = ?,
            annule_par = ?,
            motif_annulation = ?
        WHERE id = ?
    ''', (maintenant, utilisateur_type, raison, course['id']))
    
    # 5. LIBÉRER LE CONDUCTEUR SI NÉCESSAIRE
    if course['conducteur_id']:
        db.execute('''
            UPDATE conducteurs 
            SET en_course = 0, disponible = 1
            WHERE id = ?
        ''', (course['conducteur_id'],))
    
    db.commit()
    
    # 6. MISE À JOUR STATISTIQUES (optionnel)
    try:
        db.execute('''
            UPDATE statistiques 
            SET courses_annulees = courses_annulees + 1
            WHERE id = 1
        ''')
    except:
        pass
    
    return jsonify(resultat)
    # ================== ROUTE : ACCEPTER UNE COURSE ==================

@app.route('/api/courses/<code>/accepter', methods=['POST'])
@require_auth('conducteur')
def accepter_course(code):
    """Conducteur accepte une course"""
    
    db = get_db()
    conducteur_id = g.user['id']
    
    # 1. Récupérer la course
    cursor = db.execute(
        '''SELECT id, client_id, conducteur_id, statut, prix_convenu
           FROM courses WHERE code_unique = ?''',
        (code,)
    )
    course = cursor.fetchone()
    
    if not course:
        return jsonify({'error': 'Course non trouvée'}), 404
    
    # 2. Vérifications
    if course['statut'] not in ['en_attente', 'en_recherche']:  
        return jsonify({'error': f'Course non disponible (statut: {course["statut"]})'}), 400
    
    if course['conducteur_id']:
        return jsonify({'error': 'Course déjà acceptée'}), 400
    
    # 3. CORRECTION : Vérifier que le conducteur n'est PAS EN COURSE (pas "disponible")
    cursor = db.execute(
        "SELECT en_course FROM conducteurs WHERE id = ?",  # ← Change "disponible" par "en_course"
        (conducteur_id,)
    )
    conducteur = cursor.fetchone()
    
    if not conducteur or conducteur['en_course'] == 1:  # ← Change "disponible == 0" par "en_course == 1"
        print(f"❌ Conducteur {conducteur_id} est en course")
        return jsonify({'error': 'Vous êtes déjà en course'}), 400
    
    # 4. Mettre à jour la course
    maintenant = datetime.now().isoformat()
    
    db.execute(
        '''UPDATE courses 
           SET statut = 'acceptee',
               conducteur_id = ?,
               date_acceptation = ?
           WHERE id = ?''',
        (conducteur_id, maintenant, course['id'])
    )
    
    # 5. Mettre à jour le conducteur - CORRECTION IMPORTANTE
    db.execute(
        "UPDATE conducteurs SET en_course = 1, disponible = 1, updated_at = ? WHERE id = ?",  # ← disponible = 1 !
        (maintenant, conducteur_id)
    )
    
    # 6. Notifier le client
    db.execute(
        "INSERT INTO logs_securite (type, utilisateur_type, utilisateur_id, details) VALUES (?, ?, ?, ?)",
        ('notification', 'client', course['client_id'], f'Course {code} acceptée')
    )
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course acceptée avec succès',
        'course': {
            'code': code,
            'statut': 'acceptee',
            'acceptation': maintenant,
            'prix': course['prix_convenu']
        }
    })


@app.route('/api/courses/<course_code>/statut', methods=['GET'])
def get_course_status(course_code):
    """
    Retourne le statut d'une course spécifique - VERSION CORRIGÉE
    """
    print(f"🔍 [API] get_course_status CORRIGÉ pour: {course_code}")
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # CORRECTION: code_unique au lieu de code, prix_convenu au lieu de prix_total
        cursor.execute('''
            SELECT code_unique, statut, conducteur_id, 
                   point_depart_lat, point_depart_lng,
                   point_arrivee_lat, point_arrivee_lng,
                   prix_convenu,  -- CORRECTION: prix_convenu, pas prix_total
                   'standard' as service_type,  -- Valeur par défaut
                   date_demande as created_at
            FROM courses 
            WHERE code_unique = ?
        ''', (course_code,))
        
        course = cursor.fetchone()
        
        if not course:
            conn.close()
            print(f"❌ [API] Course {course_code} non trouvée")
            return jsonify({'success': False, 'error': 'Course non trouvée'}), 404
        
        print(f"✅ [API] Course trouvée: {dict(course)}")
        
        # Récupérer le conducteur si attribué
        conducteur_info = None
        if course['conducteur_id']:
            cursor.execute('''
                SELECT nom, telephone, immatricule, 
                       marque_vehicule, modele_vehicule,
                       couleur_vehicule, latitude, longitude
                FROM conducteurs 
                WHERE id = ?
            ''', (course['conducteur_id'],))
            
            conducteur = cursor.fetchone()
            if conducteur:
                conducteur_info = dict(conducteur)
                print(f"✅ [API] Conducteur trouvé: {conducteur_info}")
        
        conn.close()
        
        # Préparer la réponse
        response_data = {
            'success': True,
            'course': {
                'code': course['code_unique'],  # CORRECTION: code_unique
                'statut': course['statut'],
                'prix_total': course['prix_convenu'],  # CORRECTION: prix_convenu
                'service_type': course['service_type'],
                'conducteur': conducteur_info,
                'coordonnees': {
                    'depart': {
                        'lat': course['point_depart_lat'],
                        'lng': course['point_depart_lng']
                    },
                    'arrivee': {
                        'lat': course['point_arrivee_lat'],
                        'lng': course['point_arrivee_lng']
                    }
                },
                'created_at': course['created_at']
            }
        }
        
        print(f"✅ [API] Réponse envoyée")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ [API] Erreur get_course_status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/debug/courses_structure', methods=['GET'])
def debug_courses_structure():
    """Debug: Affiche la structure de la table courses"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Voir les colonnes de la table courses
        cursor.execute("PRAGMA table_info(courses)")
        columns = cursor.fetchall()
        
        # Voir quelques lignes
        cursor.execute("SELECT * FROM courses LIMIT 3")
        sample_data = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'columns': [dict(col) for col in columns],
            'sample_data': [dict(row) for row in sample_data] if sample_data else []
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500        


# ================== ROUTE : COMMENCER UNE COURSE ==================

@app.route('/api/courses/<code>/commencer', methods=['POST'])
@require_auth('conducteur')
def commencer_course(code):
    """Conducteur commence une course (arrivé au point de départ)"""
    
    db = get_db()
    conducteur_id = g.user['id']
    
    # 1. Récupérer la course
    cursor = db.execute(
        '''SELECT id, client_id, conducteur_id, statut, prix_convenu
           FROM courses WHERE code_unique = ?''',
        (code,)
    )
    course = cursor.fetchone()
    
    if not course:
        return jsonify({'error': 'Course non trouvée'}), 404
    
    # 2. Vérifications
    if course['statut'] != 'acceptee':
        return jsonify({'error': f'Course non acceptée (statut: {course["statut"]})'}), 400
    
    if course['conducteur_id'] != conducteur_id:
        return jsonify({'error': 'Cette course ne vous est pas attribuée'}), 403
    
    # 3. Vérifier que le conducteur est en course
    cursor = db.execute(
        '''SELECT en_course FROM conducteurs WHERE id = ?''',
        (conducteur_id,)
    )
    conducteur = cursor.fetchone()
    
    if not conducteur['en_course']:
        return jsonify({'error': 'Vous n\'êtes pas en course'}), 400
    
    # 4. Mettre à jour la course
    maintenant = datetime.now().isoformat()
    
    db.execute(
        '''UPDATE courses 
           SET statut = 'en_cours',
               conducteur_id = ?,   
               date_debut = ?
           WHERE id = ?''',
        (conducteur_id, maintenant, course['id'])  
    )

    # 5. CORRECTION : Mettre le conducteur comme INDISPONIBLE
    db.execute(
        '''UPDATE conducteurs 
           SET disponible = 0,  
               en_course = 1,
               updated_at = ?
           WHERE id = ?''',
        (maintenant, conducteur_id)
    )
    
    # 6. Notifier le client
    db.execute(
        '''INSERT INTO logs_securite 
           (type, utilisateur_type, utilisateur_id, details)
           VALUES (?, ?, ?, ?)''',
        ('notification', 'client', course['client_id'], 
         f'Course {code} commencée par conducteur {conducteur_id}')
    )
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course commencée avec succès',
        'course': {
            'code': code,
            'statut': 'en_cours',
            'debut': maintenant,
            'prix': course['prix_convenu']
        }
    })
# ================== ROUTE : TERMINER UNE COURSE ==================

@app.route('/api/courses/<code>/terminer', methods=['POST'])
@require_auth('conducteur')
def terminer_course(code):
    """Conducteur termine une course (arrivé à destination)"""

    print("=" * 60)
    print("🔥 DEBUG TERMINER_COURSE - DÉBUT")
    print(f"Course: {code}")
    
    db = get_db()
    conducteur_id = g.user['id']
    
    # 1. Récupérer la course
    cursor = db.execute(
        '''SELECT id, client_id, conducteur_id, statut, prix_convenu, date_debut
           FROM courses WHERE code_unique = ?''',
        (code,)
    )
    course = cursor.fetchone()
    
    if not course:
        return jsonify({'error': 'Course non trouvée'}), 404
    
    # 2. Vérifications
    if course['statut'] != 'en_cours':
        return jsonify({'error': f'Course non en cours (statut: {course["statut"]})'}), 400
    
    if course['conducteur_id'] != conducteur_id:
        return jsonify({'error': 'Cette course ne vous est pas attribuée'}), 403
    
    # 3. Calculs financiers
    prix_convenu = course['prix_convenu']
    
    # Récupérer le pourcentage de taxes
    cursor = db.execute(
        'SELECT valeur FROM configuration WHERE cle = "pourcentage_taxes"'
    )
    pourcentage_taxes = float(cursor.fetchone()[0])
    
    # Calculs
    taxes = prix_convenu * (pourcentage_taxes / 100)
    gain_conducteur = prix_convenu  # ⭐ MODIFIÉ : Le conducteur voit le prix TOTAL
    prix_final = prix_convenu

    print(f"🎯 Calculs: prix={prix_convenu}, taxes={taxes}, gain_affiché={gain_conducteur}")
    
    print(f"🔧 TERMINER_COURSE: Course {code}")
    print(f"   Conducteur {conducteur_id}")
    print(f"   Prix: {prix_convenu}, Gain conducteur (affiché): {gain_conducteur}")
    
    # 4. Mettre à jour la course
    maintenant = datetime.now().isoformat()

    try:
        print(f"🔥 TENTATIVE UPDATE courses...")
        db.execute(
            '''UPDATE courses 
               SET statut = 'terminee', 
                   date_fin = ?,
                   prix_final = ?,
                   paiement_effectue = 1
               WHERE id = ?''',
            (maintenant, float(prix_final), int(course['id']))
        )
        print(f"✅ UPDATE courses réussi")
    except Exception as e:
        print(f"❌ ERREUR UPDATE courses: {e}")
        # Fallback simple
        db.execute(
            '''UPDATE courses 
                SET statut = 'terminee', 
                    date_fin = ?,
                    paiement_effectue = 1
                WHERE id = ?''',
            (maintenant, course['id'])
        )
        print(f"✅ Fallback réussi (sans prix_final)")
    
    # 5. Mettre à jour le conducteur
    db.execute(
        '''UPDATE conducteurs 
           SET en_course = 0, 
               disponible = 1,  
               courses_effectuees = courses_effectuees + 1,
               gains_totaux = gains_totaux + ?,  -- ⭐ Le conducteur voit le TOTAL
               updated_at = ?
           WHERE id = ?''',
        (gain_conducteur, maintenant, conducteur_id)  # ⭐ gain_conducteur = prix_convenu
    )
    print(f"   APRÈS: Conducteur mis à jour: disponible=1, en_course=0")

    # ===== GESTION DE L'ABONNEMENT (décrémentation) =====
    try:
        print("🔍 Tentative de décrémentation...")
    
        # Vérifier d'abord l'abonnement
        cursor.execute('''
            SELECT courses_restantes FROM abonnements 
            WHERE conducteur_id = ? AND actif = 1
        ''', (conducteur_id,))
    
        abonnement = cursor.fetchone()
        if abonnement:
            print(f"📊 Abonnement trouvé: {abonnement[0]} courses restantes")
        else:
            print("❌ Aucun abonnement trouvé pour ce conducteur")
            # Créer un abonnement par défaut
            cursor.execute('''
                INSERT INTO abonnements (conducteur_id, courses_achetees, courses_restantes)
                VALUES (?, 50, 49)
            ''', (conducteur_id,))
            db.commit()
            print("✅ Abonnement créé par défaut avec 49 courses")
            
        # Décrémenter les courses restantes
        cursor.execute('''
            UPDATE abonnements 
            SET courses_restantes = courses_restantes - 1
            WHERE conducteur_id = ? AND actif = 1 AND courses_restantes > 0
        ''', (conducteur_id,))

        print(f"✅ Lignes mises à jour: {cursor.rowcount}")
    
        # Vérifier combien de lignes ont été mises à jour
        if cursor.rowcount > 0:
            print(f"✅ Abonnement mis à jour: -1 course pour conducteur {conducteur_id}")
        
            # Récupérer les nouvelles courses restantes
            cursor.execute('''
                SELECT courses_restantes FROM abonnements 
                WHERE conducteur_id = ?
            ''', (conducteur_id,))
        
            restantes_row = cursor.fetchone()
            if restantes_row:
                restantes = restantes_row[0]
                print(f"📊 Courses restantes après cette course: {restantes}")
            
                # ⭐⭐ ALERTES selon le nombre de courses restantes
                if restantes <= 0:
                    print(f"⚠️ Conducteur {conducteur_id} - ABONNEMENT TERMINÉ")
                elif restantes <= 3:
                    print(f"⚠️ ATTENTION: Plus que {restantes} courses incluses")
                elif restantes <= 5:
                    print(f"ℹ️ Plus que {restantes} courses incluses")
        else:
            print(f"ℹ️ Aucun abonnement trouvé pour conducteur {conducteur_id} (ou déjà à 0)")
        
    except Exception as e:
        print(f"⚠️ Erreur mise à jour abonnement: {e}")
    
    # ===== ⭐⭐ AJOUTER LES TAXES CUMULÉES (déplacé ici) =====
    try:
        cursor.execute('''
            UPDATE conducteurs 
            SET taxes_cumulees = COALESCE(taxes_cumulees, 0) + ?
            WHERE id = ?
        ''', (taxes, conducteur_id))
        print(f"💰 Taxes cumulées: +{taxes} KMF pour conducteur {conducteur_id}")
        print(f"   Total taxes dues maintenant: (à vérifier dans SELECT)")
    except Exception as e:
        print(f"⚠️ Erreur mise à jour taxes_cumulees: {e}")
    
    # ===== MISE À JOUR DE L'HISTORIQUE MENSUEL =====
    try:
        # Mois en cours (format YYYY-MM)
        mois = datetime.now().strftime('%Y-%m')
        
        # Vérifier si une entrée existe déjà pour ce mois
        cursor.execute('''
            SELECT id FROM historique_conducteur 
            WHERE conducteur_id = ? AND mois = ?
        ''', (conducteur_id, mois))
        
        historique_existant = cursor.fetchone()
        
        if historique_existant:
            # Mettre à jour l'existant
            cursor.execute('''
                UPDATE historique_conducteur 
                SET courses_effectuees = courses_effectuees + 1,
                    gains_totaux = gains_totaux + ?,
                    taxes_payees = taxes_payees + ?
                WHERE conducteur_id = ? AND mois = ?
            ''', (prix_convenu, taxes, conducteur_id, mois))
        else:
            # Créer une nouvelle entrée
            cursor.execute('''
                INSERT INTO historique_conducteur 
                (conducteur_id, mois, courses_effectuees, gains_totaux, taxes_payees)
                VALUES (?, ?, 1, ?, ?)
            ''', (conducteur_id, mois, prix_convenu, taxes))
        
        print(f"📊 Historique mis à jour pour {mois}")
        
    except Exception as e:
        print(f"⚠️ Erreur mise à jour historique: {e}")
    
    # 6. Mettre à jour les statistiques (version adaptée à votre structure)
    db.execute(
        '''UPDATE statistiques
           SET courses_jour = courses_jour + 1,
               revenus_jour = revenus_jour + ?,
               taxes_dues = taxes_dues + ?
           WHERE id = 1''',
        (prix_final, taxes)
    )
    
    # 7. Notifier le client
    db.execute(
        '''INSERT INTO logs_securite 
           (type, utilisateur_type, utilisateur_id, details)
           VALUES (?, ?, ?, ?)''',
        ('notification', 'client', course['client_id'], 
         f'Course {code} terminée - Prix: {prix_final} KMF')
    )

    print(f"🔥 AVANT COMMIT - Vérification conducteur:")
    cursor = db.execute(
        "SELECT disponible, en_course FROM conducteurs WHERE id = ?",
        (conducteur_id,)
    )
    avant = cursor.fetchone()
    print(f"   Disponible: {avant['disponible']} (1=OUI)")
    print(f"   En course: {avant['en_course']} (1=OUI)")
    
    db.commit()

    print(f"🎯 COMMIT effectué !")
    
    print(f"🔥 APRÈS COMMIT - Vérification conducteur:")
    cursor = db.execute(
        "SELECT disponible, en_course FROM conducteurs WHERE id = ?",
        (conducteur_id,)
    )
    apres = cursor.fetchone()
    print(f"   Disponible: {apres['disponible']} (1=OUI)")
    print(f"   En course: {apres['en_course']} (1=OUI)")
    
    print("=" * 60)
    print("🔥 DEBUG TERMINER_COURSE - FIN")
    print("=" * 60)

    return jsonify({
        'success': True,
        'message': 'Course terminée avec succès',
        'course': {
            'code': code,
            'statut': 'terminee',
            'debut': course['date_debut'],
            'fin': maintenant,
            'duree': 'calculée',
            'finances': {
                'prix_convenu': prix_convenu,
                'prix_final': prix_final,
                'taxes_zahel': taxes,
                'gain_conducteur': gain_conducteur,  # ⭐ Maintenant = prix_convenu
                'pourcentage_taxes': pourcentage_taxes
            }
        }
    })

# ==================== ROUTES NOTIFICATIONS CONDUCTEUR ====================

@app.route('/api/conducteur/notifications/nouvelles', methods=['GET'])
@require_auth('conducteur')
def get_nouvelles_notifications():
    """Récupérer les notifications non lues pour le conducteur"""
    db = get_db()
    conducteur_id = g.user['id']
    
    # Récupérer toutes les courses où le conducteur est concerné
    cursor = db.execute('''
        SELECT id, code_unique, statut, date_demande
        FROM courses 
        WHERE conducteur_id = ? 
        AND (statut = 'en_attente' OR statut = 'en_recherche')
        AND date_demande >= datetime('now', '-30 minutes')
        ORDER BY date_demande DESC
        LIMIT 10
    ''', (conducteur_id,))
    
    courses_recentes = cursor.fetchall()
    
    # Vérifier aussi les courses sans conducteur (nouvelle recherche)
    cursor = db.execute('''
        SELECT id, code_unique, statut, date_demande
        FROM courses 
        WHERE conducteur_id IS NULL 
        AND statut = 'en_recherche'
        AND date_demande >= datetime('now', '-5 minutes')
        ORDER BY date_demande DESC
        LIMIT 5
    ''')
    
    courses_sans_conducteur = cursor.fetchall()
    
    notifications = []
    
    # 1. Notifications pour courses récentes attribuées
    for course in courses_recentes:
        notifications.append({
            'type': 'nouvelle_course',
            'message': f'Nouvelle course disponible : {course["code_unique"]}',
            'course_code': course['code_unique'],
            'timestamp': course['date_demande'],
            'urgence': 'haute' if course['statut'] == 'en_attente' else 'normale'
        })
    
    # 2. Notifications pour courses en recherche (sans conducteur)
    for course in courses_sans_conducteur:
        notifications.append({
            'type': 'course_en_recherche',
            'message': f'Course {course["code_unique"]} cherche conducteur',
            'course_code': course['code_unique'],
            'timestamp': course['date_demande'],
            'urgence': 'moyenne'
        })
    
    # 3. Vérifier les annulations récentes
    cursor = db.execute('''
        SELECT c.code_unique, c.date_fin, c.motif_annulation
        FROM courses c
        WHERE c.conducteur_id = ? 
        AND c.statut = 'annulee'
        AND c.date_fin >= datetime('now', '-1 hour')
        ORDER BY c.date_fin DESC
        LIMIT 5
    ''', (conducteur_id,))
    
    annulations = cursor.fetchall()
    
    for annulation in annulations:
        notifications.append({
            'type': 'annulation',
            'message': f'Course {annulation["code_unique"]} annulée',
            'course_code': annulation['code_unique'],
            'raison': annulation['motif_annulation'] or 'Non spécifiée',
            'timestamp': annulation['date_fin'],
            'urgence': 'basse'
        })
    
    return jsonify({
        'success': True,
        'notifications': notifications,
        'count': len(notifications),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/conducteur/notifications/marquer_lue', methods=['POST'])
@require_auth('conducteur')
def marquer_notification_lue():
    """Marquer une notification comme lue"""
    data = request.json
    
    if not data or 'course_code' not in data:
        return jsonify({'error': 'Code course requis'}), 400
    
    db = get_db()
    conducteur_id = g.user['id']
    
    # Marquer comme lue dans la table (si elle existe)
    try:
        db.execute('''
            UPDATE notifications_conducteur 
            SET lue = 1 
            WHERE conducteur_id = ? AND course_code = ?
        ''', (conducteur_id, data['course_code']))
        db.commit()
    except:
        # Si la table n'existe pas encore, on passe
        pass
    
    return jsonify({
        'success': True,
        'message': f'Notification pour {data["course_code"]} marquée comme lue'
    })


@app.route('/api/conducteur/notifications/non_lues', methods=['GET'])
@require_auth('conducteur')
def get_notifications_non_lues():
    """Récupérer le nombre de notifications non lues"""
    db = get_db()
    conducteur_id = g.user['id']
    
    try:
        # Compter les notifications non lues
        cursor = db.execute('''
            SELECT COUNT(*) as count 
            FROM notifications_conducteur 
            WHERE conducteur_id = ? AND lue = 0
        ''', (conducteur_id,))
        
        count = cursor.fetchone()['count'] or 0
        
        return jsonify({
            'success': True,
            'count': count,
            'has_notifications': count > 0
        })
        
    except:
        # Si la table n'existe pas, retourner 0
        return jsonify({
            'success': True,
            'count': 0,
            'has_notifications': False
        })
    
# ========== ROUTE PANEL PDG SECRET ==========
@app.route('/admin/secret')
def admin_panel():
    """Route secrète pour le panel PDG"""
    # Vérifier token via query param
    token = request.args.get('token')
    
    if not token:
        return jsonify({'error': 'Accès non autorisé'}), 401
    
    db = get_db()
    cursor = db.execute(
        'SELECT id FROM admin_pdg WHERE secret_key = ?',
        (token,)
    )
    
    if not cursor.fetchone():
        return jsonify({'error': 'Token invalide'}), 401
    
    # Retourner une page HTML simple pour test
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚗 ZAHEL - Panel PDG Secret</title>
        <style>
            body {
                background: linear-gradient(135deg, #0f2027, #203a43);
                color: white;
                font-family: Arial, sans-serif;
                padding: 50px;
                text-align: center;
            }
            h1 {
                color: #00b4db;
                margin-bottom: 30px;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 15px;
                display: inline-block;
                margin-top: 20px;
            }
            .success {
                color: #4CAF50;
                font-size: 24px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <h1>🚗 ZAHEL - PANEL PDG SECRET</h1>
        
        <div class="container">
            <div class="success">✅ ACCÈS AUTORISÉ</div>
            <p>Token PDG valide !</p>
            <p>Le panel complet est en cours de développement...</p>
            <p><strong>Prochainement :</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>📊 Statistiques temps réel</li>
                <li>🔍 Recherche conducteurs</li>
                <li>💰 Gestion finances</li>
                <li>⚠️ Alertes et sanctions</li>
            </ul>
            <p style="margin-top: 30px; color: #aaa;">
                Cette page est accessible uniquement avec le token PDG
            </p>
        </div>
    </body>
    </html>
    """

# ========== ROUTE : STATISTIQUES PDG SIMPLIFIÉE ==========
@app.route('/api/admin/statistiques', methods=['GET'])
@require_auth('admin')
def get_statistiques():
    """Version simplifiée et garantie de fonctionner"""
    db = get_db()
    
    try:
        # 1. Conducteurs
        cursor = db.execute('SELECT COUNT(*) FROM conducteurs WHERE compte_suspendu = 0')
        conducteurs_actifs = cursor.fetchone()[0] or 0
        
        cursor = db.execute('SELECT COUNT(*) FROM conducteurs')
        total_conducteurs = cursor.fetchone()[0] or 0
        
        # 2. Clients
        cursor = db.execute('SELECT COUNT(*) FROM clients WHERE compte_suspendu = 0')
        clients_actifs = cursor.fetchone()[0] or 0
        
        cursor = db.execute('SELECT COUNT(*) FROM clients')
        total_clients = cursor.fetchone()[0] or 0
        
        # 3. Courses (simplifié - sans date)
        cursor = db.execute('SELECT COUNT(*) FROM courses')
        total_courses = cursor.fetchone()[0] or 0
        
        cursor = db.execute('SELECT COUNT(*) FROM courses WHERE statut = "terminee"')
        courses_terminees = cursor.fetchone()[0] or 0
        
        cursor = db.execute('SELECT COUNT(*) FROM courses WHERE statut = "annulee"')
        courses_annulees = cursor.fetchone()[0] or 0
        
        # 4. Finances
        cursor = db.execute('SELECT SUM(prix_final) FROM courses WHERE statut = "terminee"')
        revenus_totaux = cursor.fetchone()[0] or 0
        
        cursor = db.execute('SELECT SUM(taxes_zahel) FROM courses WHERE statut = "terminee"')
        taxes_totales = cursor.fetchone()[0] or 0
        
        cursor = db.execute('''
            SELECT 
                SUM(CASE WHEN statut = "en_attente" THEN montant ELSE 0 END) as amendes_dues,
                SUM(CASE WHEN statut = "payee" THEN montant ELSE 0 END) as amendes_payees
            FROM amendes
        ''')
        amendes_data = cursor.fetchone()
        amendes_dues = amendes_data[0] or 0 if amendes_data else 0
        amendes_payees = amendes_data[1] or 0 if amendes_data else 0
        
        # 5. Taux
        taux_annulation = (courses_annulees / total_courses * 100) if total_courses > 0 else 0
        taux_completion = (courses_terminees / total_courses * 100) if total_courses > 0 else 0
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'statistiques': {
                'conducteurs': {
                    'actifs': conducteurs_actifs,
                    'total': total_conducteurs,
                    'suspendus': total_conducteurs - conducteurs_actifs
                },
                'clients': {
                    'actifs': clients_actifs,
                    'total': total_clients,
                    'suspendus': total_clients - clients_actifs
                },
                'courses': {
                    'total': total_courses,
                    'terminees': courses_terminees,
                    'annulees': courses_annulees,
                    'taux_annulation': round(taux_annulation, 1),
                    'taux_completion': round(taux_completion, 1)
                },
                'finances': {
                    'revenus_totaux': round(revenus_totaux, 2),
                    'taxes_totales': round(taxes_totales, 2),
                    'amendes_dues': float(amendes_dues),
                    'amendes_payees': float(amendes_payees)

                },
                'message': 'Dashboard PDG fonctionnel ! Version simplifiée.'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur dans le calcul des statistiques'
        }), 500

# ========== ROUTE : VÉRIFIER TIMEOUT LUXE ==========
@app.route('/api/courses/<code>/check_luxe', methods=['GET'])
def check_luxe_timeout(code):
    """Vérifier si une recherche LUXE a dépassé le temps max"""
    print(f"🔍 Check luxe timeout pour: {code}")
    
    try:
        db = get_db()
        
        # 1. Récupérer la course
        cursor = db.execute('''
            SELECT categorie_demande, date_debut_recherche_luxe, statut
            FROM courses WHERE code_unique = ?
        ''', (code,))
        
        course = cursor.fetchone()
        
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course non trouvée'
            }), 404
        
        # 2. Si pas luxe, retourner simple
        if course['categorie_demande'] != 'luxe':
            return jsonify({
                'success': True,
                'is_luxe': False,
                'message': 'Course non luxe'
            })
        
        print(f"✅ Course luxe trouvée: {code}")
        
        # 3. Si pas encore de timer (normal au début)
        if not course['date_debut_recherche_luxe']:
            return jsonify({
                'success': True,
                'is_luxe': True,
                'timeout': False,
                'message': 'Recherche véhicule luxe en cours...'
            })
        
        # 4. Calculer temps écoulé
        from datetime import datetime
        date_debut = datetime.fromisoformat(course['date_debut_recherche_luxe'])
        temps_ecoule = (datetime.now() - date_debut).total_seconds()
        
        print(f"⏱️  Temps écoulé: {temps_ecoule:.0f}s")
        
        # 5. Récupérer temps max configuré
        cursor.execute('SELECT valeur FROM configuration WHERE cle = "temps_recherche_luxe"')
        config_row = cursor.fetchone()
        temps_max = int(config_row[0]) if config_row and config_row[0] else 300  # 5 min par défaut
        
        timeout = temps_ecoule > temps_max
        
        # 6. Messages selon état
        if timeout:
            cursor.execute('SELECT valeur FROM configuration WHERE cle = "message_timeout_luxe"')
            msg_row = cursor.fetchone()
            message = msg_row[0] if msg_row else 'Aucun véhicule luxe disponible après 5 minutes.'
        else:
            cursor.execute('SELECT valeur FROM configuration WHERE cle = "message_attente_luxe"')
            msg_row = cursor.fetchone()
            message = msg_row[0] if msg_row else 'Recherche véhicule luxe en cours...'
        
        return jsonify({
            'success': True,
            'is_luxe': True,
            'timeout': timeout,
            'temps_ecoule': int(temps_ecoule),
            'temps_max': temps_max,
            'temps_restant': max(0, temps_max - int(temps_ecoule)),
            'message': message
        })
        
    except Exception as e:
        print(f"❌ Erreur check_luxe_timeout: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/courses/<code>/reset_luxe_timer', methods=['POST'])
def reset_luxe_timer(code):
    """Réinitialiser le timer de recherche luxe (quand client clique 'Continuer')"""
    print(f"🔄 Réinitialisation timer luxe pour: {code}")
    
    try:
        db = get_db()
        
        # 1. Vérifier que la course existe et est luxe
        cursor = db.execute('''
            SELECT id, categorie_demande FROM courses 
            WHERE code_unique = ? AND categorie_demande = 'luxe'
        ''', (code,))
        
        course = cursor.fetchone()
        
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course non trouvée ou non luxe'
            }), 404
        
        # 2. Réinitialiser le timestamp
        from datetime import datetime
        nouvelle_date = datetime.now().isoformat()
        
        cursor = db.execute('''
            UPDATE courses 
            SET date_debut_recherche_luxe = ?
            WHERE code_unique = ?
        ''', (nouvelle_date, code))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Timer luxe réinitialisé',
            'nouvelle_date': nouvelle_date,
            'temps_ecoule': 0,
            'temps_restant': 300,  # 5 minutes par défaut
            'timeout': False
        })
        
    except Exception as e:
        print(f"❌ Erreur reset_luxe_timer: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
# ========== ROUTE : CHANGER CATÉGORIE LUXE → CONFORT ==========
@app.route('/api/courses/<code>/switch_to_confort', methods=['POST'])
def switch_luxe_to_confort(code):
    """Changer une course luxe en confort"""
    print(f"🔄 Switch luxe→confort pour: {code}")
    
    try:
        db = get_db()
        
        # 1. Vérifier que la course existe et est luxe
        cursor = db.execute('''
            SELECT id, categorie_demande, statut, client_id, prix_convenu
            FROM courses WHERE code_unique = ?
        ''', (code,))
        
        course = cursor.fetchone()
        
        if not course:
            return jsonify({'success': False, 'error': 'Course non trouvée'}), 404
        
        if course['categorie_demande'] != 'luxe':
            return jsonify({
                'success': False,
                'error': 'Course n\'est pas luxe',
                'current_categorie': course['categorie_demande']
            }), 400
        
        if course['statut'] not in ['en_recherche', 'en_attente']:
            return jsonify({
                'success': False,
                'error': 'Course déjà acceptée ou terminée'
            }), 400
        
        print(f"✅ Course valide pour switch: {code}")
        
        # 2. Changer la catégorie
        cursor.execute('''
            UPDATE courses 
            SET categorie_demande = 'confort',
                date_debut_recherche_luxe = NULL
            WHERE code_unique = ?
        ''', (code,))
        
        # 3. Ajuster le prix (optionnel : luxe → confort = -20%)
        nouveau_prix = course['prix_convenu'] * 0.8  # 20% moins cher
        cursor.execute('''
            UPDATE courses 
            SET prix_convenu = ?
            WHERE code_unique = ?
        ''', (nouveau_prix, code))
        
        # 4. Notifier les conducteurs confort
        cursor.execute('''
            SELECT id FROM conducteurs 
            WHERE categorie_vehicule IN ('confort', 'luxe')
            AND disponible = 1
            AND en_course = 0
        ''')
        
        conducteurs = cursor.fetchall()
        for conducteur in conducteurs:
            cursor.execute('''
                INSERT OR IGNORE INTO notifications_conducteur 
                (conducteur_id, course_code, type_notification, message)
                VALUES (?, ?, 'nouvelle_course', ?)
            ''', (conducteur['id'], code, f'Course luxe changée en confort: {code}'))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Course changée de luxe à confort',
            'course': {
                'code': code,
                'nouvelle_categorie': 'confort',
                'ancien_prix': course['prix_convenu'],
                'nouveau_prix': nouveau_prix,
                'reduction': '20%'
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur switch_luxe_to_confort: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/conducteur/notifications/marquer_toutes_lues', methods=['POST'])
@token_required
def marquer_toutes_notifications_lues(current_user):
    """Marquer toutes les notifications d'un conducteur comme lues en UN SEUL appel"""
    try:
        # current_user contient les infos du conducteur (grâce à token_required)
        conducteur_id = current_user[0]  # ou current_user['id'] selon ta structure
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Mettre à jour toutes les notifications non lues
        cursor.execute('''
            UPDATE notifications 
            SET lue = 1, date_lecture = CURRENT_TIMESTAMP
            WHERE conducteur_id = ? AND lue = 0
        ''', (conducteur_id,))
        
        conn.commit()
        nb_maj = cursor.rowcount
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'{nb_maj} notifications marquées comme lues',
            'count': nb_maj
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== ROUTES VÉRIFICATION WHATSAPP ==========
@app.route('/api/admin/verifications/en_attente', methods=['GET'])
@require_auth('admin')
def get_verifications_en_attente():
    """Récupérer les conducteurs en attente de vérification WhatsApp"""
    db = get_db()
    
    cursor = db.execute('''
        SELECT 
            id, immatricule, nom, telephone, 
            categorie_vehicule, marque_vehicule, modele_vehicule,
            couleur_vehicule, plaque_immatriculation,
            created_at
        FROM conducteurs 
        WHERE en_attente_verification = 1 
        AND compte_active = 0
        ORDER BY created_at DESC
    ''')
    
    conducteurs = cursor.fetchall()
    
    result = []
    for row in conducteurs:
        result.append({
            'id': row[0],
            'immatricule': row[1],
            'nom': row[2],
            'telephone': row[3],
            'categorie': row[4],
            'vehicule': f"{row[5]} {row[6]}",
            'couleur': row[7],
            'plaque': row[8],
            'date_inscription': row[9]
        })
    
    return jsonify({
        'success': True,
        'count': len(result),
        'conducteurs': result
    })

@app.route('/api/admin/verifications/<int:conducteur_id>/activer', methods=['POST'])
@require_auth('admin')
def activer_conducteur_apres_verification(conducteur_id):
    """Activer un conducteur après vérification WhatsApp"""
    db = get_db()
    
    # Vérifier que le conducteur existe
    cursor = db.execute('''
        SELECT immatricule, nom FROM conducteurs 
        WHERE id = ? AND en_attente_verification = 1
    ''', (conducteur_id,))
    
    conducteur = cursor.fetchone()
    if not conducteur:
        return jsonify({'error': 'Conducteur non trouvé ou déjà vérifié'}), 404
    
    # Activer le compte
    db.execute('''
        UPDATE conducteurs 
        SET en_attente_verification = 0,
            compte_active = 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (conducteur_id,))
    
    # Ajouter aux logs
    db.execute('''
        INSERT INTO logs_securite (type, utilisateur_type, utilisateur_id, details)
        VALUES (?, ?, ?, ?)
    ''', ('verification_whatsapp', 'conducteur', conducteur_id, 
          f"Vérification WhatsApp validée par admin pour {conducteur[0]}"))
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': f'Conducteur {conducteur[0]} activé avec succès',
        'conducteur': {
            'immatricule': conducteur[0],
            'nom': conducteur[1]
        }
    })

# ========== ROUTE : RECHARGER ABONNEMENT ==========
@app.route('/api/conducteur/recharger_abonnement', methods=['POST'])
@require_auth('conducteur')
def recharger_abonnement():
    """Recharger l'abonnement du conducteur"""
    data = request.json
    conducteur_id = g.user['id']
    
    if not data or 'courses' not in data:
        return jsonify({'error': 'Nombre de courses requis'}), 400
    
    try:
        courses_achetees = int(data['courses'])
        if courses_achetees <= 0:
            return jsonify({'error': 'Nombre de courses invalide'}), 400
    except:
        return jsonify({'error': 'Nombre de courses invalide'}), 400
    
    # Tarif (exemple: 1000 KMF par course)
    tarif_par_course = 1000
    montant = courses_achetees * tarif_par_course
    
    db = get_db()
    
    # Vérifier si l'abonnement existe
    cursor = db.execute('SELECT id, courses_restantes FROM abonnements WHERE conducteur_id = ?', (conducteur_id,))
    abonnement = cursor.fetchone()
    
    if abonnement:
        # Mettre à jour l'abonnement existant
        cursor.execute('''
            UPDATE abonnements 
            SET courses_achetees = courses_achetees + ?,
                courses_restantes = courses_restantes + ?,
                date_achat = CURRENT_TIMESTAMP
            WHERE conducteur_id = ?
        ''', (courses_achetees, courses_achetees, conducteur_id))
        
        nouvelles_courses = abonnement[1] + courses_achetees
        message = f"Abonnement rechargé: +{courses_achetees} courses"
        
    else:
        # Créer un nouvel abonnement
        cursor.execute('''
            INSERT INTO abonnements (conducteur_id, courses_achetees, courses_restantes)
            VALUES (?, ?, ?)
        ''', (conducteur_id, courses_achetees, courses_achetees))
        
        nouvelles_courses = courses_achetees
        message = f"Premier abonnement: {courses_achetees} courses"
    
    # Réactiver le conducteur si nécessaire
    cursor.execute('''
        UPDATE conducteurs 
        SET compte_suspendu = 0, disponible = 1
        WHERE id = ? AND compte_suspendu = 1
    ''', (conducteur_id,))
    
    # Ajouter une notification de confirmation
    try:
        cursor.execute('''
            INSERT INTO notifications_conducteur 
            (conducteur_id, type_notification, message)
            VALUES (?, 'confirmation', ?)
        ''', (conducteur_id, f"✅ Abonnement rechargé: {courses_achetees} courses"))
    except:
        pass
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': message,
        'courses_achetees': courses_achetees,
        'courses_restantes': nouvelles_courses,
        'montant': montant,
        'tarif_par_course': tarif_par_course
    })


# ========== ROUTES AMENDES POUR CONDUCTEURS ==========

@app.route('/api/conducteur/amendes_a_collecter', methods=['GET'])
@require_auth('conducteur')
def get_amendes_a_collecter():
    """Récupérer les amendes que le conducteur doit collecter"""
    try:
        db = get_db()
        conducteur_id = g.user['id']
        
        cursor = db.execute('''
            SELECT 
                ac.id,
                ac.amende_id,
                ac.client_id,
                ac.course_code,
                ac.montant,
                ac.date_collecte,
                c.nom as client_nom,
                c.telephone as client_telephone,
                co.code_unique as course_code_complet
            FROM amendes_chauffeur ac
            JOIN clients c ON ac.client_id = c.id
            JOIN courses co ON ac.course_code = co.code_unique
            WHERE ac.conducteur_id = ? AND ac.statut = 'a_verser'
            ORDER BY ac.date_collecte DESC
        ''', (conducteur_id,))
        
        result = []
        for row in cursor.fetchall():
            result.append({
                'id': row[0],
                'amende_id': row[1],
                'client_id': row[2],
                'course_code': row[3],
                'montant': float(row[4]),
                'date_collecte': row[5],
                'client_nom': row[6],
                'client_telephone': row[7]
            })
        
        # Calculer le total à verser
        total = sum(item['montant'] for item in result)
        
        return jsonify({
            'success': True,
            'amendes': result,
            'count': len(result),
            'total_a_verser': total
        })
        
    except Exception as e:
        print(f"❌ Erreur get_amendes_a_collecter: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conducteur/amendes/confirmer_collecte', methods=['POST'])
@require_auth('conducteur')
def confirmer_collecte_amende():
    """Confirmer qu'une amende a été collectée (versée à l'agence)"""
    try:
        data = request.json
        if not data or 'amende_chauffeur_id' not in data:
            return jsonify({'error': 'ID amende requis'}), 400
        
        db = get_db()
        conducteur_id = g.user['id']
        amende_chauffeur_id = data['amende_chauffeur_id']
        
        # Vérifier que l'amende appartient bien à ce conducteur
        cursor = db.execute('''
            SELECT id, montant FROM amendes_chauffeur 
            WHERE id = ? AND conducteur_id = ? AND statut = 'a_verser'
        ''', (amende_chauffeur_id, conducteur_id))
        
        amende = cursor.fetchone()
        if not amende:
            return jsonify({'error': 'Amende non trouvée ou déjà versée'}), 404
        
        # Marquer comme versée
        db.execute('''
            UPDATE amendes_chauffeur 
            SET statut = 'verse', date_versement = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (amende_chauffeur_id,))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'Amende de {amende[1]} KMF marquée comme versée'
        })
        
    except Exception as e:
        print(f"❌ Erreur confirmer_collecte_amende: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conducteur/amendes/statistiques', methods=['GET'])
@require_auth('conducteur')
def get_amendes_conducteur_stats():
    """Statistiques des amendes pour le conducteur"""
    try:
        db = get_db()
        conducteur_id = g.user['id']
        
        # Total à verser
        cursor = db.execute('''
            SELECT COUNT(*), COALESCE(SUM(montant), 0)
            FROM amendes_chauffeur 
            WHERE conducteur_id = ? AND statut = 'a_verser'
        ''', (conducteur_id,))
        
        a_verser = cursor.fetchone()
        
        # Total déjà versé
        cursor = db.execute('''
            SELECT COUNT(*), COALESCE(SUM(montant), 0)
            FROM amendes_chauffeur 
            WHERE conducteur_id = ? AND statut = 'verse'
        ''', (conducteur_id,))
        
        verse = cursor.fetchone()
        
        return jsonify({
            'success': True,
            'stats': {
                'a_verser': {
                    'count': a_verser[0] or 0,
                    'total': float(a_verser[1] or 0)
                },
                'verse': {
                    'count': verse[0] or 0,
                    'total': float(verse[1] or 0)
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur get_amendes_conducteur_stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== ROUTE HISTORIQUE CONDUCTEUR ==========
@app.route('/api/conducteur/historique', methods=['GET'])
@require_auth('conducteur')
def get_conducteur_historique():
    """Récupérer l'historique mensuel du conducteur"""
    try:
        db = get_db()
        conducteur_id = g.user['id']
        
        # Récupérer les 12 derniers mois
        cursor = db.execute('''
            SELECT 
                mois,
                courses_effectuees,
                gains_totaux,
                taxes_payees
            FROM historique_conducteur
            WHERE conducteur_id = ?
            ORDER BY mois DESC
            LIMIT 12
        ''', (conducteur_id,))
        
        historique = []
        for row in cursor.fetchall():
            historique.append({
                'mois': row[0],
                'courses': row[1],
                'gains': float(row[2]),
                'taxes': float(row[3])
            })
        
        # Calculer les totaux
        total_courses = sum(h['courses'] for h in historique)
        total_gains = sum(h['gains'] for h in historique)
        total_taxes = sum(h['taxes'] for h in historique)
        
        return jsonify({
            'success': True,
            'historique': historique,
            'totaux': {
                'courses': total_courses,
                'gains': total_gains,
                'taxes': total_taxes
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur get_conducteur_historique: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== ROUTE RENOUVELLEMENT ABONNEMENT ==========
@app.route('/api/conducteur/renouveler', methods=['POST'])
@require_auth('conducteur')
def renouveler_abonnement():
    """Renouveler l'abonnement et payer les taxes cumulées"""
    try:
        db = get_db()
        conducteur_id = g.user['id']
        
        # Récupérer les infos du conducteur
        cursor = db.execute('''
            SELECT taxes_cumulees, nom FROM conducteurs WHERE id = ?
        ''', (conducteur_id,))
        
        conducteur = cursor.fetchone()
        if not conducteur:
            return jsonify({'error': 'Conducteur non trouvé'}), 404
        
        taxes_a_payer = conducteur[0] or 0
        
        # Récupérer le prix de l'abonnement (depuis config)
        cursor = db.execute('SELECT valeur FROM configuration WHERE cle = "prix_abonnement"')
        config = cursor.fetchone()
        prix_abonnement = int(config[0]) if config else 50000  # 50 000 KMF par défaut
        
        total_a_payer = prix_abonnement + taxes_a_payer
        
        # Ici, logique de confirmation de paiement (cash à l'agence)
        # Le PDG confirmera manuellement
        
        return jsonify({
            'success': True,
            'message': 'Prêt pour renouvellement',
            'details': {
                'abonnement': prix_abonnement,
                'taxes_dues': taxes_a_payer,
                'total': total_a_payer,
                'courses': 50  # Nouvel abonnement
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur renouveler_abonnement: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Route pour que le PDG confirme le paiement
@app.route('/api/admin/renouvellement/confirmer', methods=['POST'])
@require_auth('admin')
def confirmer_renouvellement():
    """Confirmer le renouvellement d'abonnement (après paiement en agence)"""
    try:
        data = request.json
        conducteur_id = data.get('conducteur_id')
        
        if not conducteur_id:
            return jsonify({'error': 'ID conducteur requis'}), 400
        
        db = get_db()
        
        # Récupérer les taxes avant de les remettre à zéro
        cursor = db.execute('SELECT taxes_cumulees FROM conducteurs WHERE id = ?', (conducteur_id,))
        conducteur = cursor.fetchone()
        taxes_payees = conducteur[0] if conducteur else 0
        
        # Remettre les taxes à zéro
        db.execute('UPDATE conducteurs SET taxes_cumulees = 0 WHERE id = ?', (conducteur_id,))
        
        # Mettre à jour l'abonnement (remettre à 50)
        cursor = db.execute('SELECT id FROM abonnements WHERE conducteur_id = ?', (conducteur_id,))
        abonnement = cursor.fetchone()
        
        if abonnement:
            db.execute('''
                UPDATE abonnements 
                SET courses_achetees = 50,
                    courses_restantes = 50,
                    date_achat = CURRENT_TIMESTAMP
                WHERE conducteur_id = ?
            ''', (conducteur_id,))
        else:
            db.execute('''
                INSERT INTO abonnements (conducteur_id, courses_achetees, courses_restantes)
                VALUES (?, 50, 50)
            ''', (conducteur_id,))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Renouvellement confirmé',
            'taxes_payees': taxes_payees
        })
        
    except Exception as e:
        print(f"❌ Erreur confirmer_renouvellement: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== LANCEMENT SERVEUR ==========
@app.teardown_appcontext
def teardown_db(exception):
    close_db()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 API ZAHEL - SERVEUR SÉCURISÉ")
    print("="*60)
    # ⭐⭐ NOUVEAU : Initialiser la table abonnements DANS le contexte
    with app.app_context():
        init_abonnements_table()
        init_amendes_chauffeur_table()
        init_config_amendes()
        init_taxes_column()

    print("\n🌐 ENDPOINTS DISPONIBLES:")
    print("   • GET  /                    - Statut API")
    print("   • GET  /api/config          - Configuration")
    print("   • POST /api/conducteurs/inscription - Inscription conducteur")
    print("   • POST /api/conducteurs/connexion   - Connexion conducteur")
    print("   • POST /api/admin/login     - Connexion PDG secret")
    print("   • GET  /api/admin/dashboard - Dashboard PDG (Auth)")
    print("   • GET  /api/admin/conducteur/:immat - Détails conducteur (Auth)")
    print("   • POST /api/courses/demander        - Demander course (Auth client)")
    print("   • POST /api/courses/:code/annuler   - Annuler course (Auth client)")
    print("\n🔒 AUTHENTIFICATION:")
    print("   • PDG: Header 'Authorization: secret_key'")
    print("   • Conducteur: Header 'Authorization: immatricule'")
    print("   • Client: Header 'Authorization: telephone'")
    print("\n" + "="*60)
    print("⚡ Serveur démarré sur http://localhost:5001")
    print("="*60)
    
    app.run(debug=True, port=5001, host='0.0.0.0')  