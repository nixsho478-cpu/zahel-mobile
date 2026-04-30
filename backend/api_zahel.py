# -*- coding: utf-8 -*-
"""
API ZAHEL - BACKEND SÉCURISÉ - VERSION POSTGRESQL (PRODUCTION)
"""
# ⭐⭐⭐ SENTRY - Surveillance des erreurs en production ⭐⭐⭐
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://3c0ca7a66f8a88a0a10416a930c4be5a@o4511270167773184.ingest.de.sentry.io/4511270195691600",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
    environment="production"
)

from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask import render_template
import os
import hashlib
import secrets
import json
from datetime import datetime, timedelta
import math
from functools import wraps

# ⭐⭐⭐ POSTGRESQL AU LIEU DE SQLITE ⭐⭐⭐
import psycopg2
import psycopg2.extras

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = secrets.token_hex(32)

# ========== CONFIGURATION BASE DE DONNÉES ==========
# Utiliser la variable d'environnement DATABASE_URL si disponible
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://zahel:zahel2026@postgres:5432/zahel')


def get_db():
    """Obtenir la connexion à la base de données PostgreSQL"""
    if 'db' not in g:
        print(f"🔷 [API] Connexion PostgreSQL...")
        try:
            g.db = psycopg2.connect(DATABASE_URL)
            g.db.cursor_factory = psycopg2.extras.RealDictCursor
            print(f"✅ [API] Connecté à PostgreSQL")
        except Exception as e:
            print(f"❌ [API] Erreur PostgreSQL: {e}")
            raise e
    return g.db


def close_db(e=None):
    """Fermer la connexion DB"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """Helper pour exécuter des requêtes PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Convertir les placeholders ? en %s pour PostgreSQL
        query_pg = query.replace('?', '%s')
        cursor.execute(query_pg, params)
        
        if commit:
            db.commit()
            return cursor
        elif fetchone:
            return cursor.fetchone()
        elif fetchall:
            return cursor.fetchall()
        else:
            return cursor
    except Exception as e:
        print(f"❌ Erreur SQL: {e}")
        print(f"   Query: {query}")
        print(f"   Params: {params}")
        raise e


def init_abonnements_table():
    """Créer/Mettre à jour la table abonnements - Version PostgreSQL"""
    try:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            
            # 1. Créer la table si elle n'existe pas (PostgreSQL)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS abonnements (
                    id SERIAL PRIMARY KEY,
                    conducteur_id INTEGER NOT NULL UNIQUE,
                    courses_achetees INTEGER DEFAULT 50,
                    courses_restantes INTEGER DEFAULT 50,
                    date_achat TIMESTAMP DEFAULT NOW(),
                    date_expiration TIMESTAMP,
                    montant_paye DECIMAL(10,2) DEFAULT 0,
                    taxes_payees DECIMAL(10,2) DEFAULT 0,
                    statut TEXT DEFAULT 'actif',
                    mode_paiement TEXT,
                    reference_paiement TEXT,
                    date_paiement TIMESTAMP,
                    confirme_par INTEGER,
                    notes TEXT,
                    actif BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id) ON DELETE CASCADE
                )
            ''')
            
            # 2. Ajouter les colonnes manquantes (PostgreSQL)
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'abonnements'
            """)
            colonnes_existantes = [row[0] for row in cursor.fetchall()]
            
            nouvelles_colonnes = [
                ('montant_paye', 'DECIMAL(10,2) DEFAULT 0'),
                ('taxes_payees', 'DECIMAL(10,2) DEFAULT 0'),
                ('statut', 'TEXT DEFAULT ''actif'''),
                ('mode_paiement', 'TEXT'),
                ('reference_paiement', 'TEXT'),
                ('date_paiement', 'TIMESTAMP'),
                ('confirme_par', 'INTEGER'),
                ('notes', 'TEXT')
            ]
            
            for nom_colonne, type_colonne in nouvelles_colonnes:
                if nom_colonne not in colonnes_existantes:
                    try:
                        cursor.execute(f'ALTER TABLE abonnements ADD COLUMN {nom_colonne} {type_colonne}')
                        print(f"✅ Colonne '{nom_colonne}' ajoutée")
                    except Exception as e:
                        print(f"⚠️ Erreur ajout colonne {nom_colonne}: {e}")
            
            # 3. Créer un index
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_abonnements_conducteur 
                ON abonnements(conducteur_id)
            ''')
            
            db.commit()
            print("✅ Table 'abonnements' vérifiée (PostgreSQL)")
            
            # 4. Ajouter des abonnements par défaut
            cursor.execute('''
                INSERT INTO abonnements (conducteur_id, courses_achetees, courses_restantes, statut)
                SELECT id, 50, 50, 'actif' FROM conducteurs
                WHERE NOT EXISTS (
                    SELECT 1 FROM abonnements WHERE abonnements.conducteur_id = conducteurs.id
                )
                RETURNING id
            ''')
            nb_ajouts = len(cursor.fetchall())
            db.commit()
            
            if nb_ajouts > 0:
                print(f"✅ {nb_ajouts} abonnement(s) par défaut créé(s)")
            
    except Exception as e:
        print(f"❌ Erreur création table abonnements: {e}")
        import traceback
        traceback.print_exc()


def init_amendes_chauffeur_table():
    """Créer la table amendes_chauffeur - Version PostgreSQL"""
    try:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS amendes_chauffeur (
                    id SERIAL PRIMARY KEY,
                    amende_id INTEGER NOT NULL,
                    conducteur_id INTEGER NOT NULL,
                    client_id INTEGER NOT NULL,
                    course_code TEXT NOT NULL,
                    montant DECIMAL(10,2) NOT NULL,
                    date_collecte TIMESTAMP DEFAULT NOW(),
                    statut TEXT DEFAULT 'a_verser',
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
            
            db.commit()
            print("✅ Table 'amendes_chauffeur' vérifiée")
            
    except Exception as e:
        print(f"❌ Erreur création table amendes_chauffeur: {e}")


def init_config_amendes():
    """Initialiser la configuration des amendes - PostgreSQL"""
    try:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("SELECT to_regclass('configuration')")
            if not cursor.fetchone()[0]:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS configuration (
                        cle TEXT PRIMARY KEY,
                        valeur TEXT,
                        modifiable INTEGER DEFAULT 1,
                        description TEXT
                    )
                ''')
            
            config_defaut = [
                ('delai_annulation_apres_acceptation', '180', 'Délai en secondes pour annulation gratuite'),
                ('montant_amende_annulation_tardive', '500', 'Montant amende annulation tardive'),
                ('avertissements_avant_suspension', '3', 'Nombre avertissements avant suspension'),
                ('indemnisation_conducteur', '100', 'Indemnisation déplacement')
            ]
            
            for cle, valeur, desc in config_defaut:
                cursor.execute('''
                    INSERT INTO configuration (cle, valeur, description, modifiable)
                    VALUES (%s, %s, %s, 1)
                    ON CONFLICT (cle) DO NOTHING
                ''', (cle, valeur, desc))
            
            db.commit()
            print("✅ Configuration des amendes initialisée")
            
    except Exception as e:
        print(f"❌ Erreur init_config_amendes: {e}")


def init_taxes_column():
    """Ajouter la colonne taxes_cumulees - PostgreSQL"""
    try:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'conducteurs' AND column_name = 'taxes_cumulees'
            """)
            if not cursor.fetchone():
                cursor.execute('ALTER TABLE conducteurs ADD COLUMN taxes_cumulees DECIMAL(10,2) DEFAULT 0')
                print("✅ Colonne 'taxes_cumulees' ajoutée")
            
            cursor.execute("SELECT to_regclass('historique_conducteur')")
            if not cursor.fetchone()[0]:
                cursor.execute('''
                    CREATE TABLE historique_conducteur (
                        id SERIAL PRIMARY KEY,
                        conducteur_id INTEGER NOT NULL,
                        mois TEXT NOT NULL,
                        courses_effectuees INTEGER DEFAULT 0,
                        gains_totaux DECIMAL(10,2) DEFAULT 0,
                        taxes_payees DECIMAL(10,2) DEFAULT 0,
                        created_at TIMESTAMP DEFAULT NOW(),
                        FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id)
                    )
                ''')
                print("✅ Table 'historique_conducteur' créée")
            
            db.commit()
            
    except Exception as e:
        print(f"❌ Erreur init_taxes_column: {e}")


def init_champs_interruptions():
    """Ajouter les champs interruptions - PostgreSQL"""
    try:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'conducteurs' AND column_name = 'interruptions_jour'
            """)
            if not cursor.fetchone():
                cursor.execute('ALTER TABLE conducteurs ADD COLUMN interruptions_jour INTEGER DEFAULT 0')
                print("✅ Champ 'interruptions_jour' ajouté")
            
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'conducteurs' AND column_name = 'date_derniere_interruption'
            """)
            if not cursor.fetchone():
                cursor.execute('ALTER TABLE conducteurs ADD COLUMN date_derniere_interruption DATE')
                print("✅ Champ 'date_derniere_interruption' ajouté")
            
            db.commit()
            
    except Exception as e:
        print(f"⚠️ Erreur ajout champs: {e}")


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
    """Calculer distance entre deux points - Formule Haversine"""
    R = 6371000  # Rayon Terre en mètres
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2) * math.sin(delta_lat/2) + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * \
        math.sin(delta_lon/2) * math.sin(delta_lon/2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'error': 'Token manquant'}), 401
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT id, telephone FROM clients WHERE telephone = %s", (token,))
        client = cursor.fetchone()
        if client:
            return f(client, *args, **kwargs)
        
        cursor.execute("SELECT immatricule FROM conducteurs WHERE immatricule = %s", (token,))
        conducteur = cursor.fetchone()
        if conducteur:
            return f(conducteur, *args, **kwargs)
        
        return jsonify({'success': False, 'error': 'Token invalide'}), 401
    
    return decorated


# ========== MIDDLEWARE AUTH (ADAPTÉ POSTGRESQL) ==========
def require_auth(role=None):
    """Décorateur pour authentification - Version PostgreSQL"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print(f"\n🎯 DEBUG require_auth - Route: {request.path}")
            
            token = request.headers.get('Authorization')
            if not token:
                print("   ❌ Token manquant")
                return jsonify({'error': 'Token manquant'}), 401
            
            db = get_db()
            cursor = db.cursor()
            user = None
            user_type = None
            
            print(f"   Recherche utilisateur...")
            
            if role == 'admin':
                cursor.execute('SELECT * FROM admin_pdg WHERE secret_key = %s', (token,))
                user = cursor.fetchone()
                if user:
                    user_type = 'admin'
                    
            elif role == 'conducteur':
                cursor.execute('SELECT * FROM conducteurs WHERE immatricule = %s', (token,))
                user = cursor.fetchone()
                if user:
                    user_type = 'conducteur'
                    
            elif role == 'client':
                cursor.execute('SELECT * FROM clients WHERE telephone = %s', (token,))
                user = cursor.fetchone()
                if user:
                    user_type = 'client'
                    
            else:
                cursor.execute('SELECT * FROM admin_pdg WHERE secret_key = %s', (token,))
                user = cursor.fetchone()
                if user:
                    user_type = 'admin'
                
                if not user:
                    cursor.execute('SELECT * FROM conducteurs WHERE immatricule = %s', (token,))
                    user = cursor.fetchone()
                    if user:
                        user_type = 'conducteur'
                
                if not user:
                    cursor.execute('SELECT * FROM clients WHERE telephone = %s', (token,))
                    user = cursor.fetchone()
                    if user:
                        user_type = 'client'
            
            if not user:
                print(f"   ❌ Aucun utilisateur trouvé")
                return jsonify({'error': 'Token invalide'}), 401
            
            print(f"   ✅ Utilisateur trouvé : type={user_type}, id={user['id']}")
            
            user_dict = dict(user)
            user_dict['type'] = user_type
            user_dict['id'] = user['id']
            
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
    cursor = db.cursor()
    cursor.execute('SELECT cle, valeur FROM configuration WHERE modifiable = 1')
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
    """Inscription conducteur - Version PostgreSQL"""
    data = request.json
    required_fields = ['nom', 'telephone', 'password', 'nationalite', 
                      'numero_identite', 'categorie', 'marque', 'modele',
                      'couleur', 'plaque']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Champ manquant: {field}'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT id FROM conducteurs WHERE telephone = %s', (data['telephone'],))
    if cursor.fetchone():
        return jsonify({'error': 'Numéro déjà utilisé'}), 400
    
    cursor.execute('SELECT id FROM conducteurs WHERE plaque_immatriculation = %s', (data['plaque'],))
    if cursor.fetchone():
        return jsonify({'error': 'Plaque déjà enregistrée'}), 400
    
    import random
    lettres = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ', k=3))
    chiffres = ''.join(random.choices('0123456789', k=3))
    immatricule = f"ZH-{chiffres}{lettres}"
    
    categorie = data['categorie']
    if categorie in ['confort', 'luxe']:
        en_attente_verification = True
        compte_active = False
    else:
        en_attente_verification = False
        compte_active = True
    
    cursor.execute('''
        INSERT INTO conducteurs (
            immatricule, nom, telephone, password_hash, nationalite,
            numero_identite, categorie_vehicule, marque_vehicule,
            modele_vehicule, couleur_vehicule, plaque_immatriculation,
            en_attente_verification, compte_active
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (
        immatricule, data['nom'], data['telephone'], hash_password(data['password']),
        data['nationalite'], data['numero_identite'], data['categorie'],
        data['marque'], data['modele'], data['couleur'], data['plaque'],
        en_attente_verification, compte_active
    ))
    
    conducteur_id = cursor.fetchone()['id']
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


@app.route('/api/conducteur/statistiques', methods=['GET'])
@require_auth('conducteur')
def get_conducteur_statistiques():
    """Récupérer les statistiques du conducteur - Version PostgreSQL"""
    try:
        db = get_db()
        cursor = db.cursor()
        conducteur_id = g.user['id']
        
        print(f"🔍 Recherche conducteur ID: {conducteur_id}")
        
        cursor.execute('''
            SELECT 
                immatricule, nom, telephone,
                marque_vehicule, modele_vehicule, couleur_vehicule, plaque_immatriculation,
                courses_effectuees, gains_totaux, disponible, en_course,
                note_moyenne, taxes_cumulees
            FROM conducteurs 
            WHERE id = %s
        ''', (conducteur_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Conducteur non trouvé'}), 404
        
        immatricule, nom, telephone, marque, modele, couleur, plaque, \
        courses_effectuees, gains_totaux, disponible, en_course, \
        note_moyenne, taxes_cumulees = row.values()
        
        if note_moyenne is None:
            cursor.execute('''
                SELECT AVG(note_conducteur) 
                FROM courses 
                WHERE conducteur_id = %s AND statut = 'terminee' AND note_conducteur IS NOT NULL
            ''', (conducteur_id,))
            result = cursor.fetchone()
            note_moyenne = float(result['avg']) if result and result['avg'] else 5.0
        
        cursor.execute('''
            SELECT courses_restantes FROM abonnements 
            WHERE conducteur_id = %s AND statut = 'actif'
        ''', (conducteur_id,))
        abonnement = cursor.fetchone()
        
        if abonnement:
            courses_restantes = abonnement['courses_restantes']
        else:
            cursor.execute('''
                INSERT INTO abonnements (conducteur_id, courses_achetees, courses_restantes, statut)
                VALUES (%s, 50, 50, 'actif')
                RETURNING courses_restantes
            ''', (conducteur_id,))
            courses_restantes = cursor.fetchone()['courses_restantes']
            db.commit()
        
        statistiques = {
            'immatricule': immatricule,
            'nom': nom,
            'telephone': telephone,
            'vehicule': {'marque': marque, 'modele': modele, 'couleur': couleur, 'plaque': plaque},
            'performance': {
                'courses_effectuees': int(courses_effectuees or 0),
                'gains_totaux': float(gains_totaux or 0),
                'note_moyenne': float(note_moyenne or 5.0),
                'courses_restantes': int(courses_restantes),
                'taxes_cumulees': float(taxes_cumulees or 0)
            },
            'statut': {
                'disponible': bool(disponible),
                'en_course': bool(en_course)
            }
        }
        
        return jsonify({'success': True, 'conducteur': statistiques})
        
    except Exception as e:
        print(f"❌ Erreur statistiques: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conducteur/login', methods=['POST'])
def conducteur_login():
    """Connexion d'un conducteur - Version PostgreSQL avec vérification"""
    print("🎯 CONDUCTEUR LOGIN appelé")
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'Données manquantes'}), 400
    
    immatricule = data.get('immatricule')
    password = data.get('password')
    
    if not immatricule or not password:
        return jsonify({'success': False, 'error': 'Immatricule/mot de passe requis'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute(
            'SELECT id, nom, immatricule, disponible, compte_active, en_attente_verification, compte_suspendu FROM conducteurs WHERE immatricule = %s AND password_hash = %s',
            (immatricule.upper(), password_hash)
        )
        conducteur = cursor.fetchone()
        
        if not conducteur:
            return jsonify({'success': False, 'error': 'Immatricule ou mot de passe incorrect'}), 401
        
        # ⭐⭐⭐ VÉRIFICATIONS DU COMPTE ⭐⭐⭐
        if conducteur['compte_suspendu']:
            return jsonify({'success': False, 'error': 'Compte suspendu. Contactez l\'administration.'}), 403
        
        if conducteur['en_attente_verification']:
            return jsonify({'success': False, 'error': 'Compte en attente de vérification. Envoyez vos documents sur WhatsApp.'}), 403
        
        if not conducteur['compte_active']:
            return jsonify({'success': False, 'error': 'Compte non activé. Contactez l\'administration.'}), 403
        
        print(f"✅ Conducteur {immatricule} connecté")
        return jsonify({
            'success': True,
            'token': immatricule,
            'conducteur': {
                'id': conducteur['id'],
                'nom': conducteur['nom'],
                'immatricule': conducteur['immatricule'],
                'disponible': bool(conducteur['disponible'])
            }
        })
        
    except Exception as e:
        print(f"❌ ERREUR SQL conducteur_login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Erreur base de données: {str(e)}'}), 500

@app.route('/api/conducteur/toggle_status', methods=['POST'])
@require_auth('conducteur')
def toggle_conducteur_status():
    """Basculer le statut disponible/indisponible - PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    conducteur_id = g.user['id']
    
    cursor.execute('SELECT disponible FROM conducteurs WHERE id = %s', (conducteur_id,))
    conducteur = cursor.fetchone()
    
    if not conducteur:
        return jsonify({'success': False, 'error': 'Conducteur non trouvé'}), 404
    
    nouveau_statut = not conducteur['disponible']
    
    cursor.execute(
        'UPDATE conducteurs SET disponible = %s, updated_at = NOW() WHERE id = %s',
        (nouveau_statut, conducteur_id)
    )
    db.commit()
    
    return jsonify({
        'success': True,
        'disponible': nouveau_statut,
        'message': f'Statut mis à jour: {"DISPONIBLE" if nouveau_statut else "INDISPONIBLE"}'
    })


# ==================== ROUTES CLIENT ====================
@app.route('/api/client/login', methods=['POST'])
def client_login():
    """Connexion client - PostgreSQL"""
    data = request.json
    telephone = data.get('telephone')
    password = data.get('password')
    
    if not telephone or not password:
        return jsonify({'error': 'Téléphone et mot de passe requis'}), 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT id, nom, telephone, password_hash FROM clients WHERE telephone = %s',
        (telephone,)
    )
    client = cursor.fetchone()
    
    if not client:
        return jsonify({'error': 'Client non trouvé'}), 404
    
    if not verifier_password(client['password_hash'], password):
        return jsonify({'error': 'Mot de passe incorrect'}), 401
    
    return jsonify({
        'success': True,
        'token': telephone,
        'client': {
            'id': client['id'],
            'nom': client['nom'],
            'telephone': client['telephone']
        }
    })


@app.route('/api/client/register', methods=['POST'])
def client_register():
    """Inscription client - PostgreSQL"""
    data = request.json
    nom = data.get('nom')
    telephone = data.get('telephone')
    password = data.get('password')
    
    if not nom or not telephone or not password:
        return jsonify({'error': 'Tous les champs sont requis'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT id FROM clients WHERE telephone = %s', (telephone,))
    if cursor.fetchone():
        return jsonify({'error': 'Ce numéro est déjà utilisé'}), 409
    
    password_hash = hash_password(password)
    
    cursor.execute(
        'INSERT INTO clients (nom, telephone, password_hash, created_at) VALUES (%s, %s, %s, NOW()) RETURNING id',
        (nom, telephone, password_hash)
    )
    client_id = cursor.fetchone()['id']
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Client créé avec succès',
        'client': {'id': client_id, 'nom': nom, 'telephone': telephone}
    }), 201


@app.route('/api/client/courses', methods=['GET'])
@require_auth('client')
def get_client_courses():
    """Récupérer toutes les courses d'un client - PostgreSQL"""
    print("📋 API: get_client_courses appelée")
    
    try:
        db = get_db()
        cursor = db.cursor()
        client_id = g.user['id']
        
        print(f"🔍 Client ID: {client_id}")
        
        cursor.execute('''
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
            WHERE c.client_id = %s
            ORDER BY c.date_demande DESC
            LIMIT 50
        ''', (client_id,))
        
        courses = cursor.fetchall()
        print(f"✅ {len(courses)} course(s) trouvée(s)")
        
        result = []
        for row in courses:
            date_demande = row['date_demande']
            date_formatee = date_demande.strftime("%d/%m/%Y %H:%M") if date_demande else "Date inconnue"
            
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
                'date_iso': row['date_demande'].isoformat() if row['date_demande'] else None,
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
            'count': len(result)
        })
        
    except Exception as e:
        print(f"❌ Erreur get_client_courses: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== ROUTES ADRESSES FRÉQUENTES ==========
@app.route('/api/client/adresses', methods=['GET'])
@require_auth('client')
def get_client_adresses():
    """Récupérer les adresses fréquentes - PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    client_id = g.user['id']
    
    cursor.execute('''
        SELECT id, nom, adresse, latitude, longitude, type, est_principale
        FROM adresses_frequentes 
        WHERE client_id = %s
        ORDER BY est_principale DESC, type, nom
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
    """Ajouter une adresse fréquente - PostgreSQL"""
    data = request.json
    client_id = g.user['id']
    
    if not data or 'nom' not in data or 'adresse' not in data:
        return jsonify({'error': 'Nom et adresse requis'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM adresses_frequentes WHERE client_id = %s', (client_id,))
    count = cursor.fetchone()['count']
    est_principale = data.get('est_principale', count == 0)
    
    if est_principale:
        cursor.execute('UPDATE adresses_frequentes SET est_principale = FALSE WHERE client_id = %s', (client_id,))
    
    cursor.execute('''
        INSERT INTO adresses_frequentes 
        (client_id, nom, adresse, latitude, longitude, type, est_principale)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (
        client_id, data['nom'], data['adresse'],
        data.get('latitude'), data.get('longitude'),
        data.get('type', 'personnel'), est_principale
    ))
    
    adresse_id = cursor.fetchone()['id']
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Adresse ajoutée avec succès',
        'adresse_id': adresse_id,
        'est_principale': est_principale
    }), 201


@app.route('/api/client/adresses/<int:adresse_id>', methods=['DELETE'])
@require_auth('client')
def delete_client_adresse(adresse_id):
    """Supprimer une adresse fréquente - PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    client_id = g.user['id']
    
    cursor.execute('''
        SELECT est_principale FROM adresses_frequentes 
        WHERE id = %s AND client_id = %s
    ''', (adresse_id, client_id))
    
    adresse = cursor.fetchone()
    if not adresse:
        return jsonify({'error': 'Adresse non trouvée'}), 404
    
    cursor.execute('DELETE FROM adresses_frequentes WHERE id = %s AND client_id = %s', (adresse_id, client_id))
    
    if adresse['est_principale']:
        cursor.execute('SELECT id FROM adresses_frequentes WHERE client_id = %s LIMIT 1', (client_id,))
        nouvelle = cursor.fetchone()
        if nouvelle:
            cursor.execute('UPDATE adresses_frequentes SET est_principale = TRUE WHERE id = %s', (nouvelle['id'],))
    
    db.commit()
    
    return jsonify({'success': True, 'message': 'Adresse supprimée avec succès'})


@app.route('/api/client/change_password', methods=['POST'])
@require_auth('client')
def change_client_password():
    """Changer le mot de passe - PostgreSQL"""
    data = request.json
    client_id = g.user['id']
    
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Ancien et nouveau mot de passe requis'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT password_hash FROM clients WHERE id = %s', (client_id,))
    client = cursor.fetchone()
    
    if not client or not verifier_password(client['password_hash'], data['old_password']):
        return jsonify({'success': False, 'error': 'Ancien mot de passe incorrect'}), 401
    
    new_password_hash = hash_password(data['new_password'])
    cursor.execute(
        'UPDATE clients SET password_hash = %s, updated_at = NOW() WHERE id = %s',
        (new_password_hash, client_id)
    )
    db.commit()
    
    return jsonify({'success': True, 'message': 'Mot de passe modifié avec succès'})


@app.route('/api/client/amendes', methods=['GET'])
@require_auth('client')
def get_amendes_client():
    """Récupérer les amendes d'un client - PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    client_id = g.user['id']
    
    cursor.execute('''
        SELECT id, montant, raison, statut, date_amende, date_paiement
        FROM amendes 
        WHERE utilisateur_type = 'client' AND utilisateur_id = %s
        ORDER BY date_amende DESC
    ''', (client_id,))
    
    amendes = cursor.fetchall()
    
    result = []
    for amende in amendes:
        result.append({
            'id': amende['id'],
            'montant': float(amende['montant']),
            'raison': amende['raison'],
            'statut': amende['statut'],
            'date_amende': amende['date_amende'].isoformat() if amende['date_amende'] else None,
            'date_paiement': amende['date_paiement'].isoformat() if amende['date_paiement'] else None
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
    """Connexion PDG - PostgreSQL"""
    data = request.json
    
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Identifiants requis'}), 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM admin_pdg WHERE username = %s', (data['username'],))
    admin = cursor.fetchone()
    
    if not admin or not verifier_password(admin['password_hash'], data['password']):
        return jsonify({'error': 'Accès non autorisé'}), 401
    
    cursor.execute('UPDATE admin_pdg SET last_login = NOW() WHERE id = %s', (admin['id'],))
    
    cursor.execute('''
        INSERT INTO logs_securite (type, utilisateur_type, utilisateur_id, details)
        VALUES (%s, %s, %s, %s)
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


@app.route('/admin/dashboard', methods=['GET'])
def dashboard_pdg():
    """Page web du dashboard PDG"""
    token = request.args.get('token')
    
    if not token:
        return jsonify({'error': 'Accès non autorisé. Token requis.'}), 401
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id FROM admin_pdg WHERE secret_key = %s', (token,))
    
    if not cursor.fetchone():
        return jsonify({'error': 'Token invalide'}), 401
    
    return render_template('dashboard_pdg.html')


@app.route('/api/admin/conducteur/<immatricule>', methods=['GET'])
@require_auth('admin')
def get_conducteur_details(immatricule):
    """Récupérer tous les détails d'un conducteur - PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT id, immatricule, nom, telephone, email, nationalite,
               numero_identite, categorie_vehicule, marque_vehicule,
               modele_vehicule, couleur_vehicule, plaque_immatriculation,
               courses_effectuees, gains_totaux, compte_suspendu, 
               disponible, en_course, created_at, updated_at
        FROM conducteurs
        WHERE immatricule = %s
    ''', (immatricule,))
    
    conducteur = cursor.fetchone()
    
    if not conducteur:
        return jsonify({'success': False, 'error': f'Conducteur non trouvé: {immatricule}'}), 404
    
    cursor.execute('''
        SELECT code_unique, statut, prix_convenu, prix_final, date_demande,
               date_acceptation, date_debut, date_fin, note_conducteur
        FROM courses 
        WHERE conducteur_id = %s
        ORDER BY date_demande DESC
        LIMIT 10
    ''', (conducteur['id'],))
    
    historique = []
    for row in cursor.fetchall():
        historique.append({
            'code': row['code_unique'],
            'statut': row['statut'],
            'prix_convenu': float(row['prix_convenu']) if row['prix_convenu'] else 0,
            'prix_final': float(row['prix_final']) if row['prix_final'] else 0,
            'date_demande': row['date_demande'].isoformat() if row['date_demande'] else None,
            'date_acceptation': row['date_acceptation'].isoformat() if row['date_acceptation'] else None,
            'date_debut': row['date_debut'].isoformat() if row['date_debut'] else None,
            'date_fin': row['date_fin'].isoformat() if row['date_fin'] else None,
            'note': row['note_conducteur']
        })
    
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
            'performance': {
                'courses_effectuees': conducteur['courses_effectuees'],
                'gains_totaux': float(conducteur['gains_totaux']) if conducteur['gains_totaux'] else 0
            },
            'statut': {
                'suspendu': bool(conducteur['compte_suspendu']),
                'disponible': bool(conducteur['disponible']),
                'en_course': bool(conducteur['en_course'])
            },
            'historique': historique
        }
    })


@app.route('/api/conducteurs/login', methods=['POST'])
def login_conducteur():
    """Connexion conducteur (mobile) - PostgreSQL"""
    data = request.json
    
    if not data or 'immatricule' not in data or 'password' not in data:
        return jsonify({'error': 'Immatricule et mot de passe requis'}), 400
    
    immatricule = data['immatricule'].strip()
    password = data['password']
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT id, nom, telephone, password_hash, immatricule,
               compte_suspendu, disponible, en_course,
               courses_effectuees, gains_totaux 
        FROM conducteurs 
        WHERE immatricule = %s
    ''', (immatricule,))
    
    conducteur = cursor.fetchone()
    
    if not conducteur:
        return jsonify({'error': 'Conducteur non trouvé'}), 404
    
    if conducteur['compte_suspendu']:
        return jsonify({'error': 'Compte suspendu. Contactez l\'administration.'}), 403
    
    if not verifier_password(conducteur['password_hash'], password):
        return jsonify({'error': 'Mot de passe incorrect'}), 401
    
    return jsonify({
        'success': True,
        'token': conducteur['immatricule'],
        'conducteur': {
            'id': conducteur['id'],
            'immatricule': conducteur['immatricule'],
            'nom': conducteur['nom'],
            'telephone': conducteur['telephone'],
            'compte_suspendu': bool(conducteur['compte_suspendu']),
            'disponible': bool(conducteur['disponible']),
            'en_course': bool(conducteur['en_course']),
            'courses_effectuees': conducteur['courses_effectuees'],
            'gains_totaux': float(conducteur['gains_totaux']) if conducteur['gains_totaux'] else 0,
            'note_moyenne': 5.0
        },
        'message': 'Connexion réussie'
    })


@app.route('/api/conducteurs/me', methods=['GET'])
@require_auth('conducteur')
def get_conducteur_info():
    """Récupérer les informations du conducteur connecté - PostgreSQL"""
    conducteur_id = g.user['id']
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT id, immatricule, nom, telephone, email, nationalite,
               numero_identite, categorie_vehicule, marque_vehicule,
               modele_vehicule, couleur_vehicule, plaque_immatriculation,
               compte_suspendu, en_attente_verification,
               courses_effectuees, gains_totaux, disponible, en_course,
               note_moyenne, created_at, updated_at
        FROM conducteurs 
        WHERE id = %s
    ''', (conducteur_id,))
    
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
                'gains_totaux': float(conducteur['gains_totaux']) if conducteur['gains_totaux'] else 0,
                'note_moyenne': float(conducteur['note_moyenne']) if conducteur['note_moyenne'] else 5.0
            }
        }
    })


# ================== ROUTE : COURSES DISPONIBLES ==================
@app.route('/api/courses/disponibles', methods=['GET'])
@require_auth('conducteur')
def courses_disponibles():
    """Retourne les courses disponibles filtrées par catégorie - PostgreSQL"""
    print("=" * 60)
    print("🔥 DEBUG COURSES_DISPONIBLES")
    
    db = get_db()
    cursor = db.cursor()
    conducteur_id = g.user['id']
    
    print(f"Conducteur ID: {conducteur_id}")
    
    try:
        cursor.execute(
            "SELECT categorie_vehicule, disponible FROM conducteurs WHERE id = %s",
            (conducteur_id,)
        )
        conducteur = cursor.fetchone()
        
        if not conducteur:
            print("❌ Conducteur non trouvé")
            return jsonify({'error': 'Conducteur non trouvé'}), 404
        
        categorie_conducteur = conducteur['categorie_vehicule'] or 'standard'
        disponible = conducteur['disponible']
        
        if not disponible:
            return jsonify({
                'success': True,
                'count': 0,
                'courses': [],
                'message': 'Conducteur non disponible'
            })
        
        hierarchie = {
            'standard': ['standard'],
            'confort': ['standard', 'confort'],
            'luxe': ['standard', 'confort', 'luxe'],
            'moto': ['moto']
        }
        
        categories_visibles = hierarchie.get(categorie_conducteur, ['standard'])
        placeholders = ','.join(['%s' for _ in categories_visibles])
        
        query = f'''
            SELECT 
                c.id,
                c.code_unique,
                c.statut,
                c.prix_convenu,
                c.categorie_demande,
                c.point_depart_lat,
                c.point_depart_lng,
                c.point_arrivee_lat,
                c.point_arrivee_lng,
                c.adresse_depart,
                c.adresse_arrivee,
                cl.nom as client_nom,
                cl.telephone as client_telephone,
                c.date_demande,
                c.amende_incluse,
                c.montant_amende
            FROM courses c
            JOIN clients cl ON c.client_id = cl.id
            WHERE (c.statut = 'en_attente' OR c.statut = 'en_recherche')
              AND (c.conducteur_id IS NULL OR c.conducteur_id = %s)
              AND c.categorie_demande IN ({placeholders})
            ORDER BY c.date_demande DESC
            LIMIT 20
        '''
        
        params = [conducteur_id] + categories_visibles
        cursor.execute(query, params)
        courses = cursor.fetchall()
        
        print(f"📊 {len(courses)} course(s) trouvée(s)")
        
        result = []
        for row in courses:
            course_data = {
                'id': row['id'],
                'code': row['code_unique'],
                'statut': row['statut'],
                'prix_convenu': float(row['prix_convenu']) if row['prix_convenu'] else 0,
                'categorie': row['categorie_demande'],
                'distance_km': 2.5,
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
                'client': {
                    'nom': row['client_nom'],
                    'telephone': None,
                    'telephone_proxy': f"ZAHEL-{row['code_unique'][-4:]}"
                },
                'date_demande': row['date_demande'].isoformat() if row['date_demande'] else None,
                'amende_incluse': bool(row['amende_incluse']),
                'montant_amende': float(row['montant_amende']) if row['montant_amende'] else 0,
                'prix_total': float(row['prix_convenu'] or 0) + (float(row['montant_amende'] or 0))
            }
            result.append(course_data)
        
        return jsonify({
            'success': True,
            'count': len(result),
            'courses': result
        })
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ROUTE DEBUG ====================
@app.route('/api/debug/all_courses', methods=['GET'])
def debug_all_courses():
    """Debug: Affiche TOUTES les courses - PostgreSQL"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT id, code_unique, statut, conducteur_id, client_id,
                   prix_convenu, date_demande, date_acceptation
            FROM courses
            ORDER BY date_demande DESC
            LIMIT 10
        ''')
        
        courses = cursor.fetchall()
        result = [dict(row) for row in courses]
        
        return jsonify({'success': True, 'count': len(result), 'courses': result})
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== ROUTES SYSTÈME D'AMENDES ==========
@app.route('/api/amendes', methods=['GET'])
@require_auth('admin')
def get_amendes():
    """Récupérer toutes les amendes - PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    statut = request.args.get('statut', 'en_attente')
    
    try:
        cursor.execute('SELECT COUNT(*) FROM amendes WHERE statut = %s', (statut,))
        count = cursor.fetchone()['count']
        
        if count == 0:
            return jsonify({'success': True, 'amendes': [], 'total': 0, 'total_montant': 0})
        
        cursor.execute('''
            SELECT id, utilisateur_type, utilisateur_id, montant, raison, 
                   statut, date_amende, date_paiement
            FROM amendes 
            WHERE statut = %s
            ORDER BY date_amende DESC
            LIMIT 50
        ''', (statut,))
        
        amendes = []
        for row in cursor.fetchall():
            amendes.append({
                'id': row['id'],
                'utilisateur_type': row['utilisateur_type'],
                'utilisateur_id': row['utilisateur_id'],
                'nom_utilisateur': f"{row['utilisateur_type'].capitalize()} #{row['utilisateur_id']}",
                'montant': float(row['montant']) if row['montant'] else 0.0,
                'raison': row['raison'] or 'Non spécifiée',
                'statut': row['statut'],
                'date_amende': row['date_amende'].isoformat() if row['date_amende'] else None,
                'date_paiement': row['date_paiement'].isoformat() if row['date_paiement'] else None
            })
        
        total_montant = sum(a['montant'] for a in amendes)
        
        return jsonify({
            'success': True,
            'amendes': amendes,
            'total': len(amendes),
            'total_montant': total_montant
        })
        
    except Exception as e:
        print(f"💥 ERREUR: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/amendes/creer', methods=['POST'])
@require_auth('admin')
def creer_amende():
    """Créer une nouvelle amende - PostgreSQL"""
    data = request.json
    
    required = ['utilisateur_type', 'utilisateur_id', 'montant', 'raison']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Champ manquant: {field}'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    if data['utilisateur_type'] == 'client':
        cursor.execute('SELECT id FROM clients WHERE id = %s', (data['utilisateur_id'],))
    else:
        cursor.execute('SELECT id FROM conducteurs WHERE id = %s', (data['utilisateur_id'],))
    
    if not cursor.fetchone():
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    cursor.execute('''
        INSERT INTO amendes (utilisateur_type, utilisateur_id, montant, raison, statut)
        VALUES (%s, %s, %s, %s, 'en_attente')
        RETURNING id
    ''', (data['utilisateur_type'], data['utilisateur_id'], data['montant'], data['raison']))
    
    amende_id = cursor.fetchone()['id']
    
    cursor.execute('''
        INSERT INTO avertissements (utilisateur_type, utilisateur_id, type, details)
        VALUES (%s, %s, 'amende', %s)
    ''', (data['utilisateur_type'], data['utilisateur_id'], f'Amende de {data["montant"]} KMF: {data["raison"]}'))
    
    try:
        cursor.execute('UPDATE statistiques SET amendes_dues = amendes_dues + %s WHERE id = 1', (data['montant'],))
    except:
        pass
    
    db.commit()
    
    return jsonify({'success': True, 'message': 'Amende créée', 'amende_id': amende_id}), 201


@app.route('/api/amendes/<int:amende_id>/payer', methods=['POST'])
def payer_amende(amende_id):
    """Marquer une amende comme payée - PostgreSQL"""
    data = request.json
    
    if 'token_paiement' not in data:
        return jsonify({'error': 'Token de paiement requis'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM amendes WHERE id = %s', (amende_id,))
    amende = cursor.fetchone()
    
    if not amende:
        return jsonify({'error': 'Amende non trouvée'}), 404
    
    if amende['statut'] == 'payee':
        return jsonify({'error': 'Amende déjà payée'}), 400
    
    if not data['token_paiement'].startswith('PAY_'):
        return jsonify({'error': 'Token de paiement invalide'}), 400
    
    maintenant = datetime.now()
    
    cursor.execute('''
        UPDATE amendes 
        SET statut = 'payee', date_paiement = %s
        WHERE id = %s
    ''', (maintenant, amende_id))
    
    try:
        cursor.execute('''
            UPDATE statistiques 
            SET amendes_dues = amendes_dues - %s, amendes_payees = amendes_payees + %s
            WHERE id = 1
        ''', (amende['montant'], amende['montant']))
    except:
        pass
    
    if amende['utilisateur_type'] == 'client' and 'suspension' in amende['raison'].lower():
        cursor.execute('''
            UPDATE clients 
            SET compte_suspendu = FALSE, date_suspension = NULL, motif_suspension = NULL
            WHERE id = %s
        ''', (amende['utilisateur_id'],))
    
    db.commit()
    
    return jsonify({'success': True, 'message': 'Amende payée avec succès'})


@app.route('/api/amendes/<int:amende_id>/annuler', methods=['POST'])
@require_auth('admin')
def annuler_amende(amende_id):
    """Annuler une amende - PostgreSQL"""
    data = request.json
    
    if not data or 'raison' not in data:
        return jsonify({'error': 'Raison requise'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM amendes WHERE id = %s', (amende_id,))
    amende = cursor.fetchone()
    
    if not amende:
        return jsonify({'error': 'Amende non trouvée'}), 404
    
    if amende['statut'] != 'en_attente':
        return jsonify({'error': f'Amende déjà {amende["statut"]}'}), 400
    
    maintenant = datetime.now()
    cursor.execute('''
        UPDATE amendes SET statut = 'annulee', date_paiement = %s WHERE id = %s
    ''', (maintenant, amende_id))
    
    cursor.execute('''
        INSERT INTO avertissements (utilisateur_type, utilisateur_id, type, details)
        VALUES (%s, %s, 'amende_annulee', %s)
    ''', (amende['utilisateur_type'], amende['utilisateur_id'], f'Amende #{amende_id} annulée: {data["raison"]}'))
    
    try:
        cursor.execute('UPDATE statistiques SET amendes_dues = amendes_dues - %s WHERE id = 1', (amende['montant'],))
    except:
        pass
    
    db.commit()
    
    return jsonify({'success': True, 'message': f'Amende #{amende_id} annulée'})

# ========== ROUTES GESTION DES ABONNEMENTS (ADMIN) ==========

@app.route('/api/admin/abonnements', methods=['GET'])
@require_auth('admin')
def get_all_abonnements():
    """Récupérer tous les abonnements - PostgreSQL"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT 
                c.id as conducteur_id,
                c.immatricule,
                c.nom,
                c.telephone,
                c.compte_suspendu,
                c.disponible,
                c.taxes_cumulees,
                c.courses_annulees_mois,
                a.id as abonnement_id,
                a.courses_achetees,
                a.courses_restantes,
                a.date_achat,
                a.montant_paye,
                a.taxes_payees,
                a.statut as statut_abonnement,
                a.mode_paiement,
                a.date_paiement
            FROM conducteurs c
            LEFT JOIN abonnements a ON c.id = a.conducteur_id
            ORDER BY 
                CASE 
                    WHEN a.statut = 'actif' AND a.courses_restantes <= 5 THEN 1
                    WHEN a.statut = 'actif' AND a.courses_restantes <= 10 THEN 2
                    WHEN a.statut = 'actif' THEN 3
                    ELSE 4
                END,
                c.created_at DESC
        ''')
        
        result = []
        for row in cursor.fetchall():
            courses_restantes = row['courses_restantes'] if row['courses_restantes'] is not None else 0
            courses_achetees = row['courses_achetees'] if row['courses_achetees'] is not None else 0
            taxes_cumulees = float(row['taxes_cumulees'] or 0)
            
            if row['statut_abonnement'] != 'actif':
                status_color = 'gray'
                status_text = 'AUCUN'
            elif courses_restantes <= 0:
                status_color = 'danger'
                status_text = 'ÉPUISÉ'
            elif courses_restantes <= 5:
                status_color = 'warning'
                status_text = f'CRITIQUE ({courses_restantes})'
            elif courses_restantes <= 10:
                status_color = 'info'
                status_text = f'Attention ({courses_restantes})'
            else:
                status_color = 'success'
                status_text = f'ACTIF ({courses_restantes})'
            
            result.append({
                'conducteur_id': row['conducteur_id'],
                'immatricule': row['immatricule'],
                'nom': row['nom'],
                'telephone': row['telephone'],
                'compte_suspendu': bool(row['compte_suspendu']),
                'disponible': bool(row['disponible']),
                'taxes_cumulees': taxes_cumulees,
                'courses_annulees_mois': row['courses_annulees_mois'] or 0,
                'abonnement': {
                    'id': row['abonnement_id'],
                    'courses_achetees': courses_achetees,
                    'courses_restantes': courses_restantes,
                    'date_achat': row['date_achat'].isoformat() if row['date_achat'] else None,
                    'montant_paye': float(row['montant_paye'] or 0),
                    'taxes_payees': float(row['taxes_payees'] or 0),
                    'statut': row['statut_abonnement'] or 'aucun',
                    'mode_paiement': row['mode_paiement'],
                    'date_paiement': row['date_paiement'].isoformat() if row['date_paiement'] else None
                } if row['abonnement_id'] else None,
                'status_color': status_color,
                'status_text': status_text
            })
        
        return jsonify({'success': True, 'abonnements': result, 'total': len(result)})
        
    except Exception as e:
        print(f"❌ Erreur get_all_abonnements: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/abonnements/config', methods=['GET'])
@require_auth('admin')
def get_abonnements_config():
    """Récupérer la configuration - PostgreSQL"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        config = {'forfait_defaut': 50, 'prix_par_course': 1000, 'seuil_alerte': 5}
        
        try:
            cursor.execute("SELECT cle, valeur FROM configuration WHERE cle LIKE 'abonnement_%'")
            for row in cursor.fetchall():
                key = row['cle'].replace('abonnement_', '')
                if row['valeur'].isdigit():
                    config[key] = int(row['valeur'])
                else:
                    config[key] = row['valeur']
        except:
            pass
        
        return jsonify({'success': True, 'config': config})
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/abonnements/config', methods=['POST'])
@require_auth('admin')
def save_abonnements_config():
    """Sauvegarder la configuration - PostgreSQL"""
    try:
        data = request.json
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT to_regclass('configuration')")
        if not cursor.fetchone()[0]:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuration (
                    cle TEXT PRIMARY KEY,
                    valeur TEXT,
                    modifiable INTEGER DEFAULT 1,
                    description TEXT
                )
            ''')
        
        for key, value in data.items():
            cursor.execute('''
                INSERT INTO configuration (cle, valeur, modifiable)
                VALUES (%s, %s, 1)
                ON CONFLICT (cle) DO UPDATE SET valeur = EXCLUDED.valeur
            ''', (f'abonnement_{key}', str(value)))
        
        db.commit()
        return jsonify({'success': True, 'message': 'Configuration sauvegardée'})
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/abonnements/recharger', methods=['POST'])
@require_auth('admin')
def admin_recharger_abonnement():
    """Recharger l'abonnement - PostgreSQL"""
    try:
        data = request.json
        
        if not data or 'conducteur_id' not in data:
            return jsonify({'error': 'ID conducteur requis'}), 400
        
        conducteur_id = data['conducteur_id']
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT valeur FROM configuration WHERE cle = 'forfait_courses'")
        config_forfait = cursor.fetchone()
        forfait_courses = int(config_forfait['valeur']) if config_forfait else 50
        
        cursor.execute("SELECT valeur FROM configuration WHERE cle = 'prix_forfait'")
        config_prix = cursor.fetchone()
        prix_forfait = float(config_prix['valeur']) if config_prix else 1000
        
        cursor.execute('SELECT taxes_cumulees, nom FROM conducteurs WHERE id = %s', (conducteur_id,))
        conducteur = cursor.fetchone()
        if not conducteur:
            return jsonify({'error': 'Conducteur non trouvé'}), 404
        
        taxes_dues = float(conducteur['taxes_cumulees'] or 0)
        total_a_payer = prix_forfait + taxes_dues
        
        cursor.execute('SELECT id FROM abonnements WHERE conducteur_id = %s', (conducteur_id,))
        abonnement = cursor.fetchone()
        
        mode_paiement = data.get('mode_paiement', 'Espèces')
        reference = data.get('reference', '')
        
        if abonnement:
            cursor.execute('''
                UPDATE abonnements 
                SET courses_achetees = %s,
                    courses_restantes = %s,
                    date_achat = NOW(),
                    montant_paye = %s,
                    taxes_payees = %s,
                    statut = 'actif',
                    mode_paiement = %s,
                    reference_paiement = %s,
                    confirme_par = %s,
                    date_paiement = NOW()
                WHERE conducteur_id = %s
            ''', (forfait_courses, forfait_courses, total_a_payer, taxes_dues,
                  mode_paiement, reference, g.user['id'], conducteur_id))
            message = f"Abonnement renouvelé: {forfait_courses} courses"
        else:
            cursor.execute('''
                INSERT INTO abonnements 
                (conducteur_id, courses_achetees, courses_restantes, montant_paye, 
                 taxes_payees, statut, mode_paiement, reference_paiement, confirme_par)
                VALUES (%s, %s, %s, %s, %s, 'actif', %s, %s, %s)
            ''', (conducteur_id, forfait_courses, forfait_courses, total_a_payer,
                  taxes_dues, mode_paiement, reference, g.user['id']))
            message = f"Premier abonnement: {forfait_courses} courses"
        
        cursor.execute('''
            UPDATE conducteurs 
            SET taxes_cumulees = 0, courses_annulees_mois = 0 
            WHERE id = %s
        ''', (conducteur_id,))
        
        cursor.execute('''
            UPDATE conducteurs 
            SET compte_suspendu = FALSE, disponible = TRUE
            WHERE id = %s AND compte_suspendu = TRUE
        ''', (conducteur_id,))
        
        cursor.execute('''
            INSERT INTO logs_securite (type, utilisateur_type, utilisateur_id, details)
            VALUES ('renouvellement_abonnement', 'admin', %s, %s)
        ''', (g.user['id'], f"Renouvellement {forfait_courses} courses pour conducteur {conducteur_id}"))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'forfait_courses': forfait_courses,
            'prix_forfait': prix_forfait,
            'taxes_payees': taxes_dues,
            'total_paye': total_a_payer
        })
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conducteurs/stats', methods=['GET'])
def get_driver_stats():
    """Récupérer les stats des conducteurs - PostgreSQL"""
    try:
        lat = float(request.args.get('lat', -11.698))
        lng = float(request.args.get('lng', 43.256))
        radius = float(request.args.get('radius', 5))
        category = request.args.get('category', None)
    except:
        lat, lng, radius = -11.698, 43.256, 5
        category = None
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM conducteurs WHERE disponible = TRUE AND en_course = FALSE')
    total_online = cursor.fetchone()['count'] or 0
    
    cursor.execute('SELECT COUNT(*) FROM conducteurs WHERE disponible = TRUE AND en_course = FALSE')
    nearby = cursor.fetchone()['count'] or 0
    
    category_count = 0
    if category:
        cursor.execute('''
            SELECT COUNT(*) FROM conducteurs 
            WHERE disponible = TRUE AND en_course = FALSE AND categorie_vehicule = %s
        ''', (category,))
        category_count = cursor.fetchone()['count'] or 0
    
    return jsonify({
        'success': True,
        'stats': {
            'total_online': total_online,
            'nearby': nearby,
            f'category_{category}': category_count if category else 0
        }
    })
    

# ========== ROUTES COURSES ==========
@app.route('/api/courses/demander', methods=['POST'])
@require_auth('client')
def demander_course():
    """Demander une course - PostgreSQL"""
    data = request.json
    
    required_fields = ['depart_lat', 'depart_lng', 'arrivee_lat', 'arrivee_lng', 'prix']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Champ manquant: {field}'}), 400
    
    db = get_db()
    cursor = db.cursor()
    client_id = g.user['id']
    
    if g.user.get('compte_suspendu'):
        return jsonify({'error': 'Compte suspendu'}), 403
    
    code_course = generate_code_course()
    categorie_demande = data.get('categorie', 'standard')
    adresse_depart = data.get('adresse_depart')
    adresse_arrivee = data.get('adresse_arrivee') or data.get('destination', '')
    
    cursor.execute('''
        INSERT INTO courses (
            code_unique, client_id, prix_convenu, 
            point_depart_lat, point_depart_lng,
            point_arrivee_lat, point_arrivee_lng, 
            statut, categorie_demande,
            adresse_depart, adresse_arrivee
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'en_recherche', %s, %s, %s)
        RETURNING id
    ''', (
        code_course, client_id, data['prix'],
        data['depart_lat'], data['depart_lng'],
        data['arrivee_lat'], data['arrivee_lng'],
        categorie_demande, adresse_depart, adresse_arrivee
    ))
    
    course_id = cursor.fetchone()['id']
    
    cursor.execute('''
        SELECT id FROM conducteurs 
        WHERE disponible = TRUE AND en_course = FALSE AND compte_suspendu = FALSE
        LIMIT 20
    ''')
    conducteurs_dispo = cursor.fetchall()
    
    for conducteur in conducteurs_dispo:
        cursor.execute('''
            INSERT INTO notifications_conducteur 
            (conducteur_id, course_code, type_notification, message)
            VALUES (%s, %s, 'nouvelle_course', %s)
        ''', (conducteur['id'], code_course, f'Nouvelle course: {code_course} - {data["prix"]} KMF'))
    
    db.commit()
    
    return jsonify({
        'success': True,
        'course': {
            'id': course_id,
            'code': code_course,
            'statut': 'en_recherche',
            'conducteur_attribue': False,
            'conducteurs_disponibles': len(conducteurs_dispo)
        }
    }), 201


@app.route('/api/courses/<code>/annuler', methods=['POST'])
@require_auth()
def annuler_course(code):
    """Annuler une course - PostgreSQL"""
    data = request.json or {}
    raison = data.get('raison', 'non_specifie')
    
    db = get_db()
    cursor = db.cursor()
    utilisateur_id = g.user['id']
    utilisateur_type = g.user['type']
    
    cursor.execute('''
        SELECT id, client_id, conducteur_id, statut, date_acceptation
        FROM courses WHERE code_unique = %s
    ''', (code,))
    course = cursor.fetchone()
    
    if not course:
        return jsonify({'error': 'Course non trouvée'}), 404
    
    if course['statut'] in ['terminee', 'annulee']:
        return jsonify({'error': f'Course déjà {course["statut"]}'}), 400
    
    if utilisateur_type == 'client' and course['client_id'] != utilisateur_id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    if utilisateur_type == 'conducteur':
        if course['conducteur_id'] and course['conducteur_id'] != utilisateur_id:
            return jsonify({'error': 'Course déjà prise par un autre conducteur'}), 403
    
    maintenant = datetime.now()
    cursor.execute('''
        UPDATE courses 
        SET statut = 'annulee', date_fin = %s, annule_par = %s, motif_annulation = %s
        WHERE id = %s
    ''', (maintenant, utilisateur_type, raison, course['id']))
    
    if course['conducteur_id']:
        cursor.execute('''
            UPDATE conducteurs SET en_course = FALSE, disponible = TRUE WHERE id = %s
        ''', (course['conducteur_id'],))
    
    db.commit()
    
    return jsonify({
        'success': True,
        'course': code,
        'statut': 'annulee',
        'annule_par': utilisateur_type
    })


@app.route('/api/courses/<code>/accepter', methods=['POST'])
@require_auth('conducteur')
def accepter_course(code):
    """Conducteur accepte une course - PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    conducteur_id = g.user['id']
    
    cursor.execute('''
        SELECT c.id, c.client_id, c.conducteur_id, c.statut, c.prix_convenu,
               c.point_depart_lat, c.point_depart_lng,
               c.point_arrivee_lat, c.point_arrivee_lng,
               c.adresse_depart, c.adresse_arrivee
        FROM courses c
        WHERE c.code_unique = %s
    ''', (code,))
    course = cursor.fetchone()
    
    if not course:
        return jsonify({'error': 'Course non trouvée'}), 404
    
    if course['statut'] not in ['en_attente', 'en_recherche']:
        return jsonify({'error': f'Course non disponible'}), 400
    
    if course['conducteur_id']:
        return jsonify({'error': 'Course déjà acceptée'}), 400
    
    cursor.execute("SELECT en_course FROM conducteurs WHERE id = %s", (conducteur_id,))
    conducteur = cursor.fetchone()
    
    if not conducteur or conducteur['en_course']:
        return jsonify({'error': 'Vous êtes déjà en course'}), 400
    
    maintenant = datetime.now()
    
    cursor.execute('''
        UPDATE courses 
        SET statut = 'acceptee', conducteur_id = %s, date_acceptation = %s
        WHERE id = %s
    ''', (conducteur_id, maintenant, course['id']))
    
    cursor.execute(
        "UPDATE conducteurs SET en_course = TRUE, disponible = TRUE, updated_at = %s WHERE id = %s",
        (maintenant, conducteur_id)
    )
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course acceptée',
        'course': {
            'code': code,
            'statut': 'acceptee',
            'prix': float(course['prix_convenu']) if course['prix_convenu'] else 0,
            'depart': {
                'lat': course['point_depart_lat'],
                'lng': course['point_depart_lng'],
                'adresse': course['adresse_depart'] or 'Point de départ'
            },
            'arrivee': {
                'lat': course['point_arrivee_lat'],
                'lng': course['point_arrivee_lng'],
                'adresse': course['adresse_arrivee'] or 'Destination'
            }
        }
    })


@app.route('/api/courses/<course_code>/statut', methods=['GET'])
def get_course_status(course_code):
    """Retourne le statut d'une course - PostgreSQL"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT code_unique, statut, conducteur_id, 
                   point_depart_lat, point_depart_lng,
                   point_arrivee_lat, point_arrivee_lng,
                   prix_convenu, date_demande
            FROM courses 
            WHERE code_unique = %s
        ''', (course_code,))
        
        course = cursor.fetchone()
        
        if not course:
            return jsonify({'success': False, 'error': 'Course non trouvée'}), 404
        
        conducteur_info = None
        if course['conducteur_id']:
            cursor.execute('''
                SELECT nom, immatricule, 
                       marque_vehicule, modele_vehicule,
                       couleur_vehicule, plaque_immatriculation,  
                       latitude, longitude, telephone
                FROM conducteurs 
                WHERE id = %s
            ''', (course['conducteur_id'],))
            conducteur = cursor.fetchone()
            if conducteur:
                conducteur_info = dict(conducteur)
                conducteur_info['telephone'] = None
                conducteur_info['telephone_proxy'] = f"ZAHEL-{course_code[-4:]}"
        
        return jsonify({
            'success': True,
            'course': {
                'code': course['code_unique'],
                'statut': course['statut'],
                'prix_total': float(course['prix_convenu']) if course['prix_convenu'] else 0,
                'conducteur': conducteur_info,
                'coordonnees': {
                    'depart': {'lat': course['point_depart_lat'], 'lng': course['point_depart_lng']},
                    'arrivee': {'lat': course['point_arrivee_lat'], 'lng': course['point_arrivee_lng']}
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/courses/<code>/commencer', methods=['POST'])
@require_auth('conducteur')
def commencer_course(code):
    """Conducteur commence une course - PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    conducteur_id = g.user['id']
    
    cursor.execute('''
        SELECT id, client_id, conducteur_id, statut, prix_convenu
        FROM courses WHERE code_unique = %s
    ''', (code,))
    course = cursor.fetchone()
    
    if not course:
        return jsonify({'error': 'Course non trouvée'}), 404
    
    if course['statut'] != 'acceptee':
        return jsonify({'error': 'Course non acceptée'}), 400
    
    if course['conducteur_id'] != conducteur_id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    maintenant = datetime.now()
    
    cursor.execute('''
        UPDATE courses 
        SET statut = 'en_cours', date_debut = %s
        WHERE id = %s
    ''', (maintenant, course['id']))
    
    cursor.execute('''
        UPDATE conducteurs 
        SET disponible = FALSE, en_course = TRUE, updated_at = %s
        WHERE id = %s
    ''', (maintenant, conducteur_id))
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course commencée',
        'course': {'code': code, 'statut': 'en_cours'}
    })


@app.route('/api/courses/<code>/terminer', methods=['POST'])
@require_auth('conducteur')
def terminer_course(code):
    """Conducteur termine une course - PostgreSQL"""
    print("=" * 60)
    print("🔥 DEBUG TERMINER_COURSE")
    
    db = get_db()
    cursor = db.cursor()
    conducteur_id = g.user['id']
    
    cursor.execute('''
        SELECT id, client_id, conducteur_id, statut, prix_convenu
        FROM courses WHERE code_unique = %s
    ''', (code,))
    course = cursor.fetchone()
    
    if not course:
        return jsonify({'error': 'Course non trouvée'}), 404
    
    if course['statut'] != 'en_cours':
        return jsonify({'error': 'Course non en cours'}), 400
    
    if course['conducteur_id'] != conducteur_id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    prix_convenu = float(course['prix_convenu']) if course['prix_convenu'] else 0
    
    cursor.execute("SELECT valeur FROM configuration WHERE cle = 'pourcentage_taxes'")
    config_row = cursor.fetchone()
    pourcentage_taxes = float(config_row['valeur']) if config_row else 5.0
    
    taxes = prix_convenu * (pourcentage_taxes / 100)
    
    maintenant = datetime.now()
    
    cursor.execute('''
        UPDATE courses 
        SET statut = 'terminee', date_fin = %s, prix_final = %s, paiement_effectue = TRUE
        WHERE id = %s
    ''', (maintenant, prix_convenu, course['id']))
    
    cursor.execute('''
        UPDATE conducteurs 
        SET en_course = FALSE, disponible = TRUE,
            courses_effectuees = courses_effectuees + 1,
            gains_totaux = gains_totaux + %s,
            taxes_cumulees = COALESCE(taxes_cumulees, 0) + %s,
            updated_at = %s
        WHERE id = %s
    ''', (prix_convenu, taxes, maintenant, conducteur_id))
    
    # Décrémenter les courses restantes
    cursor.execute('''
        UPDATE abonnements 
        SET courses_restantes = courses_restantes - 1
        WHERE conducteur_id = %s AND statut = 'actif' AND courses_restantes > 0
    ''', (conducteur_id,))
    
    if cursor.rowcount == 0:
        cursor.execute('''
            INSERT INTO abonnements (conducteur_id, courses_achetees, courses_restantes, statut)
            VALUES (%s, 50, 49, 'actif')
            ON CONFLICT (conducteur_id) DO UPDATE
            SET courses_restantes = EXCLUDED.courses_restantes
        ''', (conducteur_id,))
    
    # Historique mensuel
    mois = maintenant.strftime('%Y-%m')
    cursor.execute('''
        INSERT INTO historique_conducteur 
        (conducteur_id, mois, courses_effectuees, gains_totaux, taxes_payees)
        VALUES (%s, %s, 1, %s, %s)
        ON CONFLICT (conducteur_id, mois) DO UPDATE
        SET courses_effectuees = historique_conducteur.courses_effectuees + 1,
            gains_totaux = historique_conducteur.gains_totaux + EXCLUDED.gains_totaux,
            taxes_payees = historique_conducteur.taxes_payees + EXCLUDED.taxes_payees
    ''', (conducteur_id, mois, prix_convenu, taxes))
    
    db.commit()
    
    print("✅ Course terminée - Statistiques mises à jour")
    
    return jsonify({
        'success': True,
        'message': 'Course terminée',
        'course': {
            'code': code,
            'statut': 'terminee',
            'finances': {
                'prix_convenu': prix_convenu,
                'prix_final': prix_convenu,
                'taxes_zahel': taxes,
                'gain_conducteur': prix_convenu,
                'pourcentage_taxes': pourcentage_taxes
            }
        }
    })

# ==================== ROUTES NOTIFICATIONS CONDUCTEUR ====================

@app.route('/api/conducteur/notifications/nouvelles', methods=['GET'])
@require_auth('conducteur')
def get_nouvelles_notifications():
    """Récupérer les notifications non lues - PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    conducteur_id = g.user['id']
    
    cursor.execute('''
        SELECT id, code_unique, statut, date_demande
        FROM courses 
        WHERE conducteur_id = %s 
        AND (statut = 'en_attente' OR statut = 'en_recherche')
        AND date_demande >= NOW() - INTERVAL '30 minutes'
        ORDER BY date_demande DESC
        LIMIT 10
    ''', (conducteur_id,))
    courses_recentes = cursor.fetchall()
    
    cursor.execute('''
        SELECT id, code_unique, statut, date_demande
        FROM courses 
        WHERE conducteur_id IS NULL 
        AND statut = 'en_recherche'
        AND date_demande >= NOW() - INTERVAL '5 minutes'
        ORDER BY date_demande DESC
        LIMIT 5
    ''')
    courses_sans_conducteur = cursor.fetchall()
    
    notifications = []
    
    for course in courses_recentes:
        notifications.append({
            'type': 'nouvelle_course',
            'message': f'Nouvelle course : {course["code_unique"]}',
            'course_code': course['code_unique'],
            'timestamp': course['date_demande'].isoformat() if course['date_demande'] else None,
            'urgence': 'haute' if course['statut'] == 'en_attente' else 'normale'
        })
    
    for course in courses_sans_conducteur:
        notifications.append({
            'type': 'course_en_recherche',
            'message': f'Course {course["code_unique"]} cherche conducteur',
            'course_code': course['code_unique'],
            'timestamp': course['date_demande'].isoformat() if course['date_demande'] else None,
            'urgence': 'moyenne'
        })
    
    cursor.execute('''
        SELECT c.code_unique, c.date_fin, c.motif_annulation
        FROM courses c
        WHERE c.conducteur_id = %s 
        AND c.statut = 'annulee'
        AND c.date_fin >= NOW() - INTERVAL '1 hour'
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
            'timestamp': annulation['date_fin'].isoformat() if annulation['date_fin'] else None,
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
    """Marquer une notification comme lue - PostgreSQL"""
    data = request.json
    
    if not data or 'course_code' not in data:
        return jsonify({'error': 'Code course requis'}), 400
    
    db = get_db()
    cursor = db.cursor()
    conducteur_id = g.user['id']
    
    try:
        cursor.execute('''
            UPDATE notifications_conducteur 
            SET lue = TRUE 
            WHERE conducteur_id = %s AND course_code = %s
        ''', (conducteur_id, data['course_code']))
        db.commit()
    except:
        pass
    
    return jsonify({'success': True, 'message': f'Notification marquée comme lue'})


@app.route('/api/conducteur/notifications/non_lues', methods=['GET'])
@require_auth('conducteur')
def get_notifications_non_lues():
    """Récupérer le nombre de notifications non lues (SANS CRÉER de nouvelles)"""
    db = get_db()
    cursor = db.cursor()
    conducteur_id = g.user['id']
    
    try:
        # ⭐ Compter UNIQUEMENT les notifications existantes non lues
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM notifications_conducteur 
            WHERE conducteur_id = %s AND lue = FALSE
        ''', (conducteur_id,))
        count = cursor.fetchone()['count'] or 0
        
        return jsonify({
            'success': True,
            'count': count,
            'has_notifications': count > 0
        })
        
    except:
        return jsonify({
            'success': True,
            'count': 0,
            'has_notifications': False
        })


@app.route('/api/conducteur/notifications/marquer_toutes_lues', methods=['POST'])
@token_required
def marquer_toutes_notifications_lues(current_user):
    """Marquer toutes les notifications comme lues - PostgreSQL"""
    try:
        conducteur_id = current_user[0]
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE notifications_conducteur 
            SET lue = TRUE, date_lecture = NOW()
            WHERE conducteur_id = %s AND lue = FALSE
        ''', (conducteur_id,))
        
        db.commit()
        nb_maj = cursor.rowcount
        
        return jsonify({'success': True, 'message': f'{nb_maj} notifications marquées', 'count': nb_maj})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== ROUTES VÉRIFICATION WHATSAPP ==========
@app.route('/api/admin/verifications/en_attente', methods=['GET'])
@require_auth('admin')
def get_verifications_en_attente():
    """Récupérer les conducteurs en attente - PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT 
            id, immatricule, nom, telephone, 
            categorie_vehicule, marque_vehicule, modele_vehicule,
            couleur_vehicule, plaque_immatriculation,
            created_at
        FROM conducteurs 
        WHERE en_attente_verification = TRUE AND compte_active = FALSE
        ORDER BY created_at DESC
    ''')
    
    conducteurs = cursor.fetchall()
    
    result = []
    for row in conducteurs:
        result.append({
            'id': row['id'],
            'immatricule': row['immatricule'],
            'nom': row['nom'],
            'telephone': row['telephone'],
            'categorie': row['categorie_vehicule'],
            'vehicule': f"{row['marque_vehicule']} {row['modele_vehicule']}",
            'couleur': row['couleur_vehicule'],
            'plaque': row['plaque_immatriculation'],
            'date_inscription': row['created_at'].isoformat() if row['created_at'] else None
        })
    
    return jsonify({'success': True, 'count': len(result), 'conducteurs': result})


@app.route('/api/admin/verifications/<int:conducteur_id>/activer', methods=['POST'])
@require_auth('admin')
def activer_conducteur_apres_verification(conducteur_id):
    """Activer un conducteur après vérification - PostgreSQL"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT immatricule, nom FROM conducteurs 
        WHERE id = %s AND en_attente_verification = TRUE
    ''', (conducteur_id,))
    conducteur = cursor.fetchone()
    
    if not conducteur:
        return jsonify({'error': 'Conducteur non trouvé ou déjà vérifié'}), 404
    
    cursor.execute('''
        UPDATE conducteurs 
        SET en_attente_verification = FALSE, compte_active = TRUE, updated_at = NOW()
        WHERE id = %s
    ''', (conducteur_id,))
    
    cursor.execute('''
        INSERT INTO logs_securite (type, utilisateur_type, utilisateur_id, details)
        VALUES (%s, %s, %s, %s)
    ''', ('verification_whatsapp', 'conducteur', conducteur_id, 
          f"Vérification WhatsApp validée pour {conducteur['immatricule']}"))
    
    db.commit()
    
    return jsonify({
        'success': True,
        'message': f'Conducteur {conducteur["immatricule"]} activé',
        'conducteur': {'immatricule': conducteur['immatricule'], 'nom': conducteur['nom']}
    })


# ========== ROUTES AMENDES POUR CONDUCTEURS ==========
@app.route('/api/conducteur/amendes_a_collecter', methods=['GET'])
@require_auth('conducteur')
def get_amendes_a_collecter():
    """Récupérer les amendes à collecter - PostgreSQL"""
    try:
        db = get_db()
        cursor = db.cursor()
        conducteur_id = g.user['id']
        
        cursor.execute('''
            SELECT 
                ac.id, ac.amende_id, ac.client_id, ac.course_code, ac.montant, ac.date_collecte,
                c.nom as client_nom, c.telephone as client_telephone
            FROM amendes_chauffeur ac
            JOIN clients c ON ac.client_id = c.id
            WHERE ac.conducteur_id = %s AND ac.statut = 'a_verser'
            ORDER BY ac.date_collecte DESC
        ''', (conducteur_id,))
        
        result = []
        for row in cursor.fetchall():
            result.append({
                'id': row['id'],
                'amende_id': row['amende_id'],
                'client_id': row['client_id'],
                'course_code': row['course_code'],
                'montant': float(row['montant']),
                'date_collecte': row['date_collecte'].isoformat() if row['date_collecte'] else None,
                'client_nom': row['client_nom'],
                'client_telephone': row['client_telephone']
            })
        
        total = sum(item['montant'] for item in result)
        
        return jsonify({'success': True, 'amendes': result, 'count': len(result), 'total_a_verser': total})
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conducteur/amendes/confirmer_collecte', methods=['POST'])
@require_auth('conducteur')
def confirmer_collecte_amende():
    """Confirmer qu'une amende a été collectée - PostgreSQL"""
    try:
        data = request.json
        if not data or 'amende_chauffeur_id' not in data:
            return jsonify({'error': 'ID amende requis'}), 400
        
        db = get_db()
        cursor = db.cursor()
        conducteur_id = g.user['id']
        amende_chauffeur_id = data['amende_chauffeur_id']
        
        cursor.execute('''
            SELECT id, montant FROM amendes_chauffeur 
            WHERE id = %s AND conducteur_id = %s AND statut = 'a_verser'
        ''', (amende_chauffeur_id, conducteur_id))
        amende = cursor.fetchone()
        
        if not amende:
            return jsonify({'error': 'Amende non trouvée ou déjà versée'}), 404
        
        cursor.execute('''
            UPDATE amendes_chauffeur 
            SET statut = 'verse', date_versement = NOW()
            WHERE id = %s
        ''', (amende_chauffeur_id,))
        
        db.commit()
        
        return jsonify({'success': True, 'message': f'Amende de {amende["montant"]} KMF marquée comme versée'})
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conducteur/amendes/statistiques', methods=['GET'])
@require_auth('conducteur')
def get_amendes_conducteur_stats():
    """Statistiques des amendes - PostgreSQL"""
    try:
        db = get_db()
        cursor = db.cursor()
        conducteur_id = g.user['id']
        
        cursor.execute('''
            SELECT COUNT(*), COALESCE(SUM(montant), 0)
            FROM amendes_chauffeur 
            WHERE conducteur_id = %s AND statut = 'a_verser'
        ''', (conducteur_id,))
        a_verser = cursor.fetchone()
        
        cursor.execute('''
            SELECT COUNT(*), COALESCE(SUM(montant), 0)
            FROM amendes_chauffeur 
            WHERE conducteur_id = %s AND statut = 'verse'
        ''', (conducteur_id,))
        verse = cursor.fetchone()
        
        return jsonify({
            'success': True,
            'stats': {
                'a_verser': {'count': a_verser['count'] or 0, 'total': float(a_verser['coalesce'] or 0)},
                'verse': {'count': verse['count'] or 0, 'total': float(verse['coalesce'] or 0)}
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== ROUTE HISTORIQUE CONDUCTEUR ==========
@app.route('/api/conducteur/historique', methods=['GET'])
@require_auth('conducteur')
def get_conducteur_historique():
    """Récupérer l'historique mensuel - PostgreSQL"""
    try:
        db = get_db()
        cursor = db.cursor()
        conducteur_id = g.user['id']
        
        cursor.execute('''
            SELECT mois, courses_effectuees, gains_totaux, taxes_payees
            FROM historique_conducteur
            WHERE conducteur_id = %s
            ORDER BY mois DESC
            LIMIT 12
        ''', (conducteur_id,))
        
        historique = []
        for row in cursor.fetchall():
            historique.append({
                'mois': row['mois'],
                'courses': row['courses_effectuees'],
                'gains': float(row['gains_totaux']),
                'taxes': float(row['taxes_payees'])
            })
        
        total_courses = sum(h['courses'] for h in historique)
        total_gains = sum(h['gains'] for h in historique)
        total_taxes = sum(h['taxes'] for h in historique)
        
        return jsonify({
            'success': True,
            'historique': historique,
            'totaux': {'courses': total_courses, 'gains': total_gains, 'taxes': total_taxes}
        })
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== ROUTE RENOUVELLEMENT ABONNEMENT ==========
@app.route('/api/conducteur/renouveler', methods=['POST'])
@require_auth('conducteur')
def renouveler_abonnement():
    """Renouveler l'abonnement - PostgreSQL"""
    try:
        db = get_db()
        cursor = db.cursor()
        conducteur_id = g.user['id']
        
        cursor.execute('SELECT taxes_cumulees, nom FROM conducteurs WHERE id = %s', (conducteur_id,))
        conducteur = cursor.fetchone()
        
        if not conducteur:
            return jsonify({'error': 'Conducteur non trouvé'}), 404
        
        taxes_a_payer = float(conducteur['taxes_cumulees'] or 0)
        
        cursor.execute('SELECT valeur FROM configuration WHERE cle = %s', ('prix_abonnement',))
        config = cursor.fetchone()
        prix_abonnement = int(config['valeur']) if config else 50000
        
        total_a_payer = prix_abonnement + taxes_a_payer
        
        return jsonify({
            'success': True,
            'message': 'Prêt pour renouvellement',
            'details': {'abonnement': prix_abonnement, 'taxes_dues': taxes_a_payer, 'total': total_a_payer, 'courses': 50}
        })
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/renouvellement/confirmer', methods=['POST'])
@require_auth('admin')
def confirmer_renouvellement_v2():
    """Confirmer le paiement et renouveler - PostgreSQL"""
    try:
        data = request.json
        conducteur_id = data.get('conducteur_id')
        montant = data.get('montant')
        mode_paiement = data.get('mode_paiement', 'Espèces')
        reference = data.get('reference', '')
        notes = data.get('notes', '')
        envoyer_whatsapp = data.get('envoyer_whatsapp', True)
        
        if not conducteur_id or not montant:
            return jsonify({'error': 'Données manquantes'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT immatricule, nom, telephone, taxes_cumulees
            FROM conducteurs WHERE id = %s
        ''', (conducteur_id,))
        conducteur = cursor.fetchone()
        
        if not conducteur:
            return jsonify({'error': 'Conducteur non trouvé'}), 404
        
        cursor.execute('''
            SELECT cle, valeur FROM configuration 
            WHERE cle IN ('forfait_courses', 'prix_forfait')
        ''')
        config = {row['cle']: row['valeur'] for row in cursor.fetchall()}
        
        forfait_courses = int(config.get('forfait_courses', 50))
        prix_forfait = float(config.get('prix_forfait', 1000))
        taxes_payees = float(conducteur['taxes_cumulees'] or 0)
        
        cursor.execute('SELECT id FROM abonnements WHERE conducteur_id = %s', (conducteur_id,))
        abonnement_existant = cursor.fetchone()
        
        if abonnement_existant:
            cursor.execute('''
                UPDATE abonnements 
                SET courses_achetees = %s, courses_restantes = %s, date_achat = NOW(),
                    montant_paye = %s, taxes_payees = %s, statut = 'actif',
                    mode_paiement = %s, reference_paiement = %s, confirme_par = %s,
                    notes = %s, date_paiement = NOW()
                WHERE conducteur_id = %s
            ''', (forfait_courses, forfait_courses, montant, taxes_payees,
                  mode_paiement, reference, g.user['id'], notes, conducteur_id))
        else:
            cursor.execute('''
                INSERT INTO abonnements 
                (conducteur_id, courses_achetees, courses_restantes, montant_paye, 
                 taxes_payees, statut, mode_paiement, reference_paiement, confirme_par, notes)
                VALUES (%s, %s, %s, %s, %s, 'actif', %s, %s, %s, %s)
            ''', (conducteur_id, forfait_courses, forfait_courses, montant,
                  taxes_payees, mode_paiement, reference, g.user['id'], notes))
        
        cursor.execute('''
            UPDATE conducteurs 
            SET taxes_cumulees = 0, courses_annulees_mois = 0 
            WHERE id = %s
        ''', (conducteur_id,))
        
        cursor.execute('''
            UPDATE conducteurs 
            SET compte_suspendu = FALSE, disponible = TRUE 
            WHERE id = %s AND compte_suspendu = TRUE
        ''', (conducteur_id,))
        
        cursor.execute('''
            INSERT INTO logs_securite (type, utilisateur_type, utilisateur_id, details)
            VALUES ('renouvellement_abonnement', 'admin', %s, %s)
        ''', (g.user['id'], f"Renouvellement forfait {forfait_courses} courses pour {conducteur['immatricule']}"))
        
        db.commit()
        
        whatsapp_url = None
        if envoyer_whatsapp and conducteur['telephone']:
            cursor.execute('SELECT valeur FROM configuration WHERE cle = %s', ('message_recu_abonnement',))
            config_msg = cursor.fetchone()
            message_template = config_msg['valeur'] if config_msg else "✅ ZAHEL - Paiement confirmé !\n\nForfait {courses} courses: {montant} KMF"
            
            message = message_template.replace('{courses}', str(forfait_courses))
            message = message.replace('{montant}', str(int(prix_forfait)))
            message = message.replace('{taxes}', str(int(taxes_payees)))
            message = message.replace('{total}', str(int(montant)))
            
            import urllib.parse
            telephone_clean = ''.join(filter(str.isdigit, conducteur['telephone']))
            message_encoded = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{telephone_clean}?text={message_encoded}"
        
        return jsonify({
            'success': True,
            'message': 'Renouvellement confirmé',
            'conducteur': {'immatricule': conducteur['immatricule'], 'nom': conducteur['nom']},
            'abonnement': {'courses': forfait_courses, 'montant': montant, 'taxes_payees': taxes_payees},
            'whatsapp_url': whatsapp_url,
            'recu_envoye': envoyer_whatsapp
        })
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== ROUTES ADMIN ==========
@app.route('/api/admin/conducteurs', methods=['GET'])
@require_auth('admin')
def get_all_conducteurs():
    """Récupérer la liste complète des conducteurs - PostgreSQL"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT immatricule, nom, telephone, categorie_vehicule as categorie,
                   courses_effectuees as courses, gains_totaux as gains,
                   disponible, en_course, compte_suspendu
            FROM conducteurs
            ORDER BY created_at DESC
        ''')
        
        conducteurs = []
        for row in cursor.fetchall():
            conducteurs.append({
                'immatricule': row['immatricule'],
                'nom': row['nom'],
                'telephone': row['telephone'],
                'categorie': row['categorie'] or 'standard',
                'courses': row['courses'] or 0,
                'gains': float(row['gains']) if row['gains'] else 0,
                'disponible': bool(row['disponible']),
                'en_course': bool(row['en_course']),
                'compte_suspendu': bool(row['compte_suspendu'])
            })
        
        return jsonify({'success': True, 'conducteurs': conducteurs, 'total': len(conducteurs)})
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/clients', methods=['GET'])
@require_auth('admin')
def get_all_clients():
    """Récupérer la liste complète des clients - PostgreSQL"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT id, nom, telephone, compte_suspendu
            FROM clients
            ORDER BY id DESC
            LIMIT 100
        ''')
        
        clients = []
        for row in cursor.fetchall():
            clients.append({
                'id': row['id'],
                'nom': row['nom'] or 'Client sans nom',
                'telephone': row['telephone'] or 'Numéro inconnu',
                'courses': 0,
                'depenses': 0,
                'compte_suspendu': bool(row['compte_suspendu'])
            })
        
        return jsonify({'success': True, 'clients': clients, 'total': len(clients)})
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/verify-password', methods=['POST'])
def verify_admin_password():
    """Vérifier le mot de passe PDG"""
    data = request.json
    password = data.get('password')
    
    if not password:
        return jsonify({'success': False, 'error': 'Mot de passe requis'}), 400
    
    ADMIN_PASSWORD = "zahel2025"
    
    if password == ADMIN_PASSWORD:
        TOKEN = "cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b"
        return jsonify({'success': True, 'token': TOKEN, 'message': 'Connexion réussie'})
    else:
        return jsonify({'success': False, 'error': 'Mot de passe incorrect'}), 401


# ========== ROUTE : POSITION CONDUCTEUR ==========
@app.route('/api/conducteur/position', methods=['POST'])
@require_auth('conducteur')
def update_conducteur_position():
    """Mettre à jour la position GPS - PostgreSQL"""
    data = request.json
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    if not lat or not lng:
        return jsonify({'error': 'Coordonnées manquantes'}), 400
    
    db = get_db()
    cursor = db.cursor()
    conducteur_id = g.user['id']
    
    cursor.execute('''
        UPDATE conducteurs 
        SET latitude = %s, longitude = %s, last_position_update = NOW()
        WHERE id = %s
    ''', (lat, lng, conducteur_id))
    db.commit()
    
    return jsonify({'success': True, 'message': 'Position mise à jour'})


# ========== CONFIGURATION ==========
def init_configuration():
    """Initialiser la configuration par défaut - PostgreSQL"""
    try:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("SELECT to_regclass('configuration')")
            if not cursor.fetchone()[0]:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS configuration (
                        cle TEXT PRIMARY KEY,
                        valeur TEXT,
                        modifiable INTEGER DEFAULT 1,
                        description TEXT,
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                ''')
            
            config_defaut = [
                ('forfait_courses', '50', 'Nombre de courses par forfait'),
                ('prix_forfait', '1000', 'Prix du forfait en KMF'),
                ('pourcentage_taxes', '5', 'Pourcentage de taxes ZAHEL'),
                ('whatsapp_agence', '2693608657', 'Numéro WhatsApp agence'),
                ('message_recu_abonnement', '✅ ZAHEL - Paiement confirmé !', 'Message reçu WhatsApp')
            ]
            
            for cle, valeur, desc in config_defaut:
                cursor.execute('''
                    INSERT INTO configuration (cle, valeur, description)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (cle) DO NOTHING
                ''', (cle, valeur, desc))
            
            db.commit()
            print("✅ Configuration par défaut initialisée")
            
    except Exception as e:
        print(f"⚠️ Erreur init_configuration: {e}")


def init_annulations_table():
    """Créer la table des annulations - PostgreSQL"""
    try:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("SELECT to_regclass('annulations_conducteur')")
            if not cursor.fetchone()[0]:
                cursor.execute('''
                    CREATE TABLE annulations_conducteur (
                        id SERIAL PRIMARY KEY,
                        conducteur_id INTEGER NOT NULL,
                        course_code TEXT NOT NULL,
                        raison TEXT,
                        date_annulation TIMESTAMP DEFAULT NOW(),
                        FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id)
                    )
                ''')
                db.commit()
                print("✅ Table annulations_conducteur créée")
    except Exception as e:
        print(f"⚠️ Erreur: {e}")


@app.route('/api/conducteur/verifier_statut', methods=['GET'])
@require_auth('conducteur')
def verifier_statut_conducteur():
    """Vérifier le statut du conducteur"""
    try:
        db = get_db()
        cursor = db.cursor()
        conducteur_id = g.user['id']
        
        cursor.execute('''
            SELECT en_course, disponible FROM conducteurs WHERE id = %s
        ''', (conducteur_id,))
        conducteur = cursor.fetchone()
        
        if not conducteur:
            return jsonify({'success': False, 'error': 'Conducteur non trouvé'}), 404
        
        return jsonify({
            'success': True,
            'peut_accepter': not conducteur['en_course'],
            'en_course': conducteur['en_course'],
            'message': 'OK' if not conducteur['en_course'] else 'Déjà en course'
        })
        
    except Exception as e:
        print(f"❌ Erreur verifier_statut: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== LANCEMENT SERVEUR ==========
@app.teardown_appcontext
def teardown_db(exception):
    close_db()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 API ZAHEL - SERVEUR SÉCURISÉ (POSTGRESQL)")
    print("="*60)
    
    with app.app_context():
        init_abonnements_table()
        init_amendes_chauffeur_table()
        init_config_amendes()
        init_taxes_column()
        init_champs_interruptions()
        init_configuration()
        init_annulations_table()
    
    print("\n🌐 ENDPOINTS DISPONIBLES:")
    print("   • GET  /                    - Statut API")
    print("   • GET  /api/config          - Configuration")
    print("   • POST /api/conducteurs/inscription - Inscription conducteur")
    print("   • POST /api/client/login    - Connexion client")
    print("   • POST /api/admin/login     - Connexion PDG")
    print("\n" + "="*60)
    print("⚡ Serveur démarré sur http://0.0.0.0:5001")
    print("="*60)
    
    app.run(debug=False, port=5001, host='0.0.0.0')