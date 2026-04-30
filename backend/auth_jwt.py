"""
Système d'authentification JWT pour ZAHEL
Remplace le système actuel basé sur immatricule/téléphone
"""
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g
import hashlib
import secrets

# Clé secrète pour JWT (à changer en production)
JWT_SECRET_KEY = secrets.token_hex(32)
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

class AuthService:
    """Service d'authentification JWT"""
    
    @staticmethod
    def generate_token(user_id, user_type, additional_data=None):
        """
        Générer un token JWT
        :param user_id: ID de l'utilisateur
        :param user_type: 'client', 'conducteur', 'admin'
        :param additional_data: Données supplémentaires à inclure
        :return: Token JWT
        """
        payload = {
            'user_id': user_id,
            'user_type': user_type,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.datetime.utcnow()
        }
        
        if additional_data:
            payload.update(additional_data)
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token):
        """
        Vérifier un token JWT
        :param token: Token JWT
        :return: Payload décodé ou None si invalide
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token expiré
        except jwt.InvalidTokenError:
            return None  # Token invalide
    
    @staticmethod
    def hash_password(password):
        """
        Hasher un mot de passe avec salting
        :param password: Mot de passe en clair
        :return: Hash sécurisé
        """
        # Générer un salt aléatoire
        salt = secrets.token_hex(16)
        # Hasher le mot de passe + salt
        hash_obj = hashlib.sha256(f"{password}{salt}".encode())
        # Format: algorithm$salt$hash
        return f"sha256${salt}${hash_obj.hexdigest()}"
    
    @staticmethod
    def verify_password(password, password_hash):
        """
        Vérifier un mot de passe
        :param password: Mot de passe en clair
        :param password_hash: Hash stocké
        :return: True si valide, False sinon
        """
        try:
            # Extraire les parties du hash
            parts = password_hash.split('$')
            if len(parts) != 3:
                return False
            
            algorithm, salt, stored_hash = parts
            
            if algorithm != 'sha256':
                return False
            
            # Recréer le hash avec le même salt
            hash_obj = hashlib.sha256(f"{password}{salt}".encode())
            return hash_obj.hexdigest() == stored_hash
        except:
            return False
    
    @staticmethod
    def require_auth(role=None):
        """
        Décorateur pour l'authentification JWT
        :param role: Rôle requis ('client', 'conducteur', 'admin') ou None pour tout rôle
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Récupérer le token depuis l'en-tête Authorization
                auth_header = request.headers.get('Authorization')
                
                if not auth_header:
                    return jsonify({
                        'success': False,
                        'error': 'Token manquant',
                        'message': 'Authentification requise'
                    }), 401
                
                # Extraire le token (format: Bearer <token>)
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
                else:
                    token = auth_header
                
                # Vérifier le token
                payload = AuthService.verify_token(token)
                
                if not payload:
                    return jsonify({
                        'success': False,
                        'error': 'Token invalide ou expiré',
                        'message': 'Veuillez vous reconnecter'
                    }), 401
                
                # Vérifier le rôle si spécifié
                if role and payload.get('user_type') != role:
                    return jsonify({
                        'success': False,
                        'error': 'Accès non autorisé',
                        'message': f'Rôle {role} requis'
                    }), 403
                
                # Stocker les informations de l'utilisateur dans g (contexte Flask)
                g.user = {
                    'id': payload['user_id'],
                    'type': payload['user_type'],
                    'token_payload': payload
                }
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def migrate_old_password(old_hash):
        """
        Migrer un ancien hash SHA-256 vers le nouveau format avec salt
        :param old_hash: Ancien hash SHA-256 simple
        :return: Nouveau hash avec salt
        """
        # Pour les anciens mots de passe, on génère un nouveau salt
        salt = secrets.token_hex(16)
        # Le hash stocké devient le "mot de passe" pour le nouveau système
        hash_obj = hashlib.sha256(f"{old_hash}{salt}".encode())
        return f"sha256${salt}${hash_obj.hexdigest()}"


# Fonctions utilitaires pour l'API
def get_current_user():
    """Récupérer l'utilisateur courant depuis le contexte Flask"""
    return g.user if hasattr(g, 'user') else None

def get_current_user_id():
    """Récupérer l'ID de l'utilisateur courant"""
    user = get_current_user()
    return user['id'] if user else None

def get_current_user_type():
    """Récupérer le type de l'utilisateur courant"""
    user = get_current_user()
    return user['type'] if user else None

# Test du module
if __name__ == '__main__':
    # Test de génération et vérification de token
    token = AuthService.generate_token(123, 'client', {'nom': 'Test Client'})
    print(f"Token généré: {token}")
    
    payload = AuthService.verify_token(token)
    print(f"Payload décodé: {payload}")
    
    # Test de hash de mot de passe
    password = "monmotdepasse"
    hashed = AuthService.hash_password(password)
    print(f"Mot de passe hashé: {hashed}")
    
    # Test de vérification
    is_valid = AuthService.verify_password(password, hashed)
    print(f"Vérification: {is_valid}")
    
    # Test avec mauvais mot de passe
    is_invalid = AuthService.verify_password("mauvais", hashed)
    print(f"Vérification avec mauvais mot de passe: {is_invalid}")