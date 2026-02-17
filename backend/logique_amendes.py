# backend/logique_amendes.py
"""
Module de logique métier pour le système d'amendes ZAHEL
Implémente les règles business spécifiques
"""

from datetime import datetime, timedelta

class SystemeAmendes:
    """Gestion des amendes et sanctions selon les règles ZAHEL"""
    
    def __init__(self, db):
        self.db = db
    
    def traiter_annulation_client(self, client_id, temps_ecoule_secondes, prix_course=None):
        """
        Traiter une annulation client selon les règles 3 strikes
        
        Règles :
        1. < 60s : Annulation gratuite
        2. > 60s :
           - 1ère : Avertissement
           - 2ème : Suspension 24h
           - 3ème : Amende 500 KMF + suspension permanente
        """
        resultat = {
            'action': None,
            'message': '',
            'amende': 0,
            'suspension': None,
            'avertissement': False
        }
        
        # Règle 1 : Annulation dans les 60 secondes
        if temps_ecoule_secondes <= 60:
            resultat['action'] = 'gratuite'
            resultat['message'] = 'Annulation dans le délai gratuit'
            return resultat
        
        # Règle 2 : Annulation après 60 secondes
        # Récupérer le nombre d'avertissements existants
        cursor = self.db.execute(
            'SELECT avertissements_annulation FROM clients WHERE id = ?',
            (client_id,)
        )
        client = cursor.fetchone()
        
        if not client:
            return {'error': 'Client non trouvé'}
        
        avertissements = client[0] if client[0] else 0
        nouvel_avertissement = avertissements + 1
        
        # Appliquer les règles 3 strikes
        if nouvel_avertissement == 1:
            # Premier avertissement
            resultat.update({
                'action': 'avertissement',
                'avertissement': True,
                'message': f"1er avertissement – Il vous reste 2 marge(s) d'erreur"
            })
            
        elif nouvel_avertissement == 2:
            # Deuxième avertissement – Suspension 24h
            date_fin = datetime.now() + timedelta(hours=24)
            resultat.update({
                'action': 'suspension_temporelle',
                'suspension': date_fin.isoformat(),
                'message': '2ème avertissement – Compte suspendu 24h'
            })
            
        elif nouvel_avertissement >= 3:
            # Troisième avertissement – Amende + suspension
            resultat.update({
                'action': 'amende_suspension',
                'amende': 500.00,
                'suspension': 'permanente',
                'message': '3ème avertissement – Amende 500 KMF + suspension'
            })
        
        # Mettre à jour la base de données
        self.db.execute(
            'UPDATE clients SET avertissements_annulation = ? WHERE id = ?',
            (nouvel_avertissement, client_id)
        )
        
        # Si amende, la créer
        if resultat['amende'] > 0:
            self.creer_amende(
                utilisateur_type='client',
                utilisateur_id=client_id,
                montant=resultat['amende'],
                raison=f'Annulation abusive ({nouvel_avertissement}ème infraction)'
            )
        
        # Si suspension, l'appliquer
        if resultat['suspension']:
            duree_heures = 24 if nouvel_avertissement == 2 else None
            self.appliquer_suspension(
                utilisateur_type='client',
                utilisateur_id=client_id,
                raison='Annulations abusives répétées',
                duree_heures=duree_heures
            )
        
        return resultat
    
    def traiter_client_absent(self, client_id, conducteur_id, prix_convenu, temps_attente_minutes):
        """
        Traiter un client absent (> 10 minutes)
        
        Règles :
        - Conducteur reçoit course gratuite
        - Client paye 50% du prix convenu
        - Compte client suspendu jusqu'au paiement
        """
        resultat = {
            'compensation_conducteur': False,
            'amende_client': 0,
            'suspension_client': True,
            'message': ''
        }
        
        if temps_attente_minutes > 10:
            # Client absent > 10min
            amende = prix_convenu * 0.5  # 50% du prix
            
            # 1. Conducteur reçoit une course gratuite
            self.db.execute(
                '''UPDATE conducteurs
                SET courses_gratuites = courses_gratuites + 1
                WHERE id = ?''',
                (conducteur_id,)
            )
            
            # 2. Amende pour le client
            self.creer_amende(
                utilisateur_type='client',
                utilisateur_id=client_id,
                montant=amende,
                raison=f'Client absent après {temps_attente_minutes} minutes d\'attente'
            )
            
            # 3. Suspension du client
            self.appliquer_suspension(
                utilisateur_type='client',
                utilisateur_id=client_id,
                raison='Client absent à la prise en charge',
                duree_heures=None  # Suspension jusqu'au paiement
            )
            
            resultat.update({
                'compensation_conducteur': True,
                'amende_client': amende,
                'message': f'Client absent > 10min. Amende : {amende} KMF (50% du prix)'
            })
        else:
            # Client absent < 10min – pas de compensation
            resultat['message'] = 'Temps d\'attente insuffisant pour compensation'
        
        return resultat
    
    def creer_amende(self, utilisateur_type, utilisateur_id, montant, raison):
        """Créer une amende dans la base"""
        cursor = self.db.execute(
            '''INSERT INTO amendes (utilisateur_type, utilisateur_id, montant, raison, statut)
            VALUES (?, ?, ?, ?, 'en_attente')''',
            (utilisateur_type, utilisateur_id, montant, raison)
        )
        
        # Mettre à jour les statistiques
        try:
            self.db.execute(
                '''UPDATE statistiques
                SET amendes_dues = amendes_dues + ?
                WHERE id = 1''',
                (montant,)
            )
        except:
            pass  # Ignorer si la colonne n'existe pas
        
        return cursor.lastrowid
    
    def appliquer_suspension(self, utilisateur_type, utilisateur_id, raison, duree_heures=None):
        """Appliquer une suspension à un utilisateur"""
        date_fin = None
        if duree_heures:
            date_fin = (datetime.now() + timedelta(hours=duree_heures)).isoformat()
        
        # Ajouter à la table suspensions
        self.db.execute(
            '''INSERT INTO suspensions (utilisateur_type, utilisateur_id, raison, duree_heures, date_fin)
            VALUES (?, ?, ?, ?, ?)''',
            (utilisateur_type, utilisateur_id, raison, duree_heures, date_fin)
        )
        
        # Mettre à jour le statut de l'utilisateur
        if utilisateur_type == 'client':
            self.db.execute(
                '''UPDATE clients
                SET compte_suspendu = 1,
                    date_suspension = ?,
                    motif_suspension = ?
                WHERE id = ?''',
                (datetime.now().isoformat(), raison, utilisateur_id)
            )
        else:
            self.db.execute(
                '''UPDATE conducteurs
                SET compte_suspendu = 1
                WHERE id = ?''',
                (utilisateur_id,)
            )