"""
Services métier pour ZAHEL
Centralisation de la logique métier pour éviter la duplication
"""
import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from auth_jwt import AuthService

class DatabaseService:
    """Service de base de données"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"
    
    def get_connection(self):
        """Obtenir une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query, params=(), fetch_one=False, fetch_all=False):
        """Exécuter une requête SQL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = cursor.lastrowid
            
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_user_by_credentials(self, identifier, password, user_type):
        """
        Authentifier un utilisateur
        :param identifier: Téléphone (client) ou immatricule (conducteur)
        :param password: Mot de passe
        :param user_type: 'client' ou 'conducteur'
        :return: (user_id, user_data) ou (None, None)
        """
        if user_type == 'client':
            query = "SELECT id, password_hash FROM clients WHERE telephone = ?"
        elif user_type == 'conducteur':
            query = "SELECT id, password_hash FROM conducteurs WHERE immatricule = ?"
        else:
            return None, None
        
        result = self.execute_query(query, (identifier,), fetch_one=True)
        
        if not result:
            return None, None
        
        user_id = result['id']
        password_hash = result['password_hash']
        
        # Vérifier le mot de passe
        if AuthService.verify_password(password, password_hash):
            return user_id, self.get_user_details(user_id, user_type)
        
        return None, None
    
    def get_user_details(self, user_id, user_type):
        """Obtenir les détails d'un utilisateur"""
        if user_type == 'client':
            query = """
                SELECT id, telephone, nom, email, 
                       avertissements_annulation, compte_suspendu,
                       created_at
                FROM clients WHERE id = ?
            """
        elif user_type == 'conducteur':
            query = """
                SELECT id, immatricule, nom, telephone, email,
                       categorie_vehicule, marque_vehicule, modele_vehicule,
                       plaque_immatriculation, disponible, en_course,
                       courses_effectuees, gains_totaux, compte_active,
                       latitude, longitude
                FROM conducteurs WHERE id = ?
            """
        else:
            return None
        
        return self.execute_query(query, (user_id,), fetch_one=True)


class CourseService:
    """Service de gestion des courses"""
    
    def __init__(self, db_service=None):
        self.db = db_service or DatabaseService()
    
    def create_course(self, client_id, depart_lat, depart_lng, arrivee_lat, arrivee_lng, prix_convenu, **kwargs):
        """Créer une nouvelle course"""
        import uuid
        
        course_code = f"ZAHEL-{uuid.uuid4().hex[:8].upper()}"
        
        query = """
            INSERT INTO courses (
                code_unique, client_id, depart_lat, depart_lng,
                arrivee_lat, arrivee_lng, prix_convenu, statut,
                date_demande
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'en_attente', CURRENT_TIMESTAMP)
        """
        
        course_id = self.db.execute_query(
            query,
            (course_code, client_id, depart_lat, depart_lng, 
             arrivee_lat, arrivee_lng, prix_convenu)
        )
        
        return {
            'course_id': course_id,
            'course_code': course_code,
            'success': True
        }
    
    def find_available_drivers(self, latitude, longitude, radius_meters=5000, vehicle_type=None):
        """Trouver des conducteurs disponibles dans un rayon"""
        # Cette requête utilise une approximation simple
        # En production, utiliser des calculs de distance plus précis
        query = """
            SELECT id, nom, telephone, categorie_vehicule,
                   marque_vehicule, modele_vehicule,
                   latitude, longitude,
                   courses_effectuees, gains_totaux
            FROM conducteurs
            WHERE disponible = 1 
              AND en_course = 0
              AND compte_active = 1
              AND compte_suspendu = 0
        """
        
        params = []
        
        if vehicle_type:
            query += " AND categorie_vehicule = ?"
            params.append(vehicle_type)
        
        drivers = self.db.execute_query(query, params, fetch_all=True)
        
        # Filtrer par distance (approximation simple)
        available_drivers = []
        for driver in drivers:
            if driver['latitude'] and driver['longitude']:
                # Calcul de distance simplifié (formule de Haversine approximée)
                lat_diff = abs(driver['latitude'] - latitude)
                lng_diff = abs(driver['longitude'] - longitude)
                
                # Approximation: 1 degré ≈ 111 km
                distance_km = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 111
                
                if distance_km * 1000 <= radius_meters:
                    available_drivers.append(dict(driver))
        
        return available_drivers
    
    def assign_driver_to_course(self, course_id, driver_id):
        """Assigner un conducteur à une course"""
        query = """
            UPDATE courses 
            SET conducteur_id = ?, statut = 'attente_acceptation',
                date_acceptation = CURRENT_TIMESTAMP
            WHERE id = ? AND statut = 'en_attente'
        """
        
        rows_affected = self.db.execute_query(query, (driver_id, course_id))
        
        if rows_affected:
            # Mettre à jour le statut du conducteur
            self.db.execute_query(
                "UPDATE conducteurs SET en_course = 1 WHERE id = ?",
                (driver_id,)
            )
            
            # Créer une notification pour le conducteur
            self.create_notification(
                driver_id, 
                'course_disponible',
                f'Nouvelle course disponible - ID: {course_id}'
            )
            
            return True
        
        return False


class NotificationService:
    """Service de notifications"""
    
    def __init__(self, db_service=None):
        self.db = db_service or DatabaseService()
    
    def create_notification(self, driver_id, notification_type, message, course_code=None):
        """Créer une notification pour un conducteur"""
        query = """
            INSERT INTO notifications_conducteur 
            (conducteur_id, course_code, type_notification, message)
            VALUES (?, ?, ?, ?)
        """
        
        return self.db.execute_query(
            query,
            (driver_id, course_code, notification_type, message)
        )
    
    def get_unread_notifications(self, driver_id, limit=10):
        """Récupérer les notifications non lues d'un conducteur"""
        query = """
            SELECT id, course_code, type_notification, message,
                   created_at
            FROM notifications_conducteur
            WHERE conducteur_id = ? AND lue = 0
            ORDER BY created_at DESC
            LIMIT ?
        """
        
        return self.db.execute_query(
            query, (driver_id, limit), fetch_all=True
        )
    
    def mark_as_read(self, notification_id):
        """Marquer une notification comme lue"""
        query = """
            UPDATE notifications_conducteur
            SET lue = 1, date_lecture = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        
        return self.db.execute_query(query, (notification_id,))


class FineService:
    """Service de gestion des amendes"""
    
    def __init__(self, db_service=None):
        self.db = db_service or DatabaseService()
    
    def create_fine(self, user_type, user_id, amount, reason, course_code=None):
        """Créer une amende"""
        query = """
            INSERT INTO amendes 
            (utilisateur_type, utilisateur_id, montant, raison, statut)
            VALUES (?, ?, ?, ?, 'en_attente')
        """
        
        fine_id = self.db.execute_query(
            query, (user_type, user_id, amount, reason)
        )
        
        # Si c'est une amende liée à une course, créer une entrée dans amendes_chauffeur
        if course_code and user_type == 'client':
            # Trouver le conducteur de la course
            course_query = """
                SELECT conducteur_id FROM courses 
                WHERE code_unique = ? AND client_id = ?
            """
            course = self.db.execute_query(
                course_query, (course_code, user_id), fetch_one=True
            )
            
            if course and course['conducteur_id']:
                self.create_driver_fine_entry(
                    fine_id, course['conducteur_id'], user_id, 
                    course_code, amount
                )
        
        return fine_id
    
    def create_driver_fine_entry(self, fine_id, driver_id, client_id, course_code, amount):
        """Créer une entrée dans amendes_chauffeur"""
        query = """
            INSERT INTO amendes_chauffeur
            (amende_id, conducteur_id, client_id, course_code, montant)
            VALUES (?, ?, ?, ?, ?)
        """
        
        return self.db.execute_query(
            query, (fine_id, driver_id, client_id, course_code, amount)
        )
    
    def get_user_fines(self, user_type, user_id, status=None):
        """Récupérer les amendes d'un utilisateur"""
        query = """
            SELECT id, montant, raison, statut, date_amende, date_paiement
            FROM amendes
            WHERE utilisateur_type = ? AND utilisateur_id = ?
        """
        
        params = [user_type, user_id]
        
        if status:
            query += " AND statut = ?"
            params.append(status)
        
        query += " ORDER BY date_amende DESC"
        
        return self.db.execute_query(query, params, fetch_all=True)


class StatisticsService:
    """Service de statistiques"""
    
    def __init__(self, db_service=None):
        self.db = db_service or DatabaseService()
    
    def update_daily_statistics(self):
        """Mettre à jour les statistiques quotidiennes"""
        # Compter les courses du jour
        today = datetime.now().strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                COUNT(*) as total_courses,
                SUM(prix_final) as total_revenue,
                SUM(taxes_zahel) as total_taxes
            FROM courses
            WHERE DATE(date_demande) = ?
              AND statut = 'terminee'
        """
        
        result = self.db.execute_query(query, (today,), fetch_one=True)
        
        # Mettre à jour les statistiques
        update_query = """
            UPDATE statistiques 
            SET courses_jour = ?, revenus_jour = ?, taxes_dues = ?,
                derniere_mise_a_jour = CURRENT_TIMESTAMP
            WHERE id = 1
        """
        
        self.db.execute_query(
            update_query,
            (
                result['total_courses'] or 0,
                result['total_revenue'] or 0,
                result['total_taxes'] or 0
            )
        )
    
    def get_dashboard_stats(self):
        """Récupérer les statistiques pour le dashboard"""
        query = """
            SELECT 
                courses_jour, courses_semaine, courses_mois,
                revenus_jour, revenus_semaine, revenus_mois,
                taxes_dues, taxes_payees,
                amendes_dues, amendes_payees,
                derniere_mise_a_jour
            FROM statistiques
            WHERE id = 1
        """
        
        return self.db.execute_query(query, fetch_one=True)


# Test des services
if __name__ == '__main__':
    print("🧪 Test des services ZAHEL")
    print("=" * 50)
    
    # Test DatabaseService
    db_service = DatabaseService()
    print("✅ DatabaseService initialisé")
    
    # Test CourseService
    course_service = CourseService(db_service)
    print("✅ CourseService initialisé")
    
    # Test NotificationService
    notification_service = NotificationService(db_service)
    print("✅ NotificationService initialisé")
    
    # Test FineService
    fine_service = FineService(db_service)
    print("✅ FineService initialisé")
    
    # Test StatisticsService
    stats_service = StatisticsService(db_service)
    print("✅ StatisticsService initialisé")
    
    print("\n🎉 Tous les services sont prêts!")