# init_abonnements_v2.py - VERSION CORRIGÉE
import sqlite3
import os

db_path = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"

print("=" * 60)
print("🔄 INITIALISATION DES ABONNEMENTS (V2)")
print("=" * 60)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # ⭐ IMPORTANT : pour accéder par nom de colonne
cursor = conn.cursor()

# Récupérer tous les conducteurs actifs
cursor.execute('''
    SELECT id, immatricule, nom FROM conducteurs 
    WHERE compte_active = 1 OR compte_active IS NULL
''')
conducteurs = cursor.fetchall()
print(f"📋 {len(conducteurs)} conducteurs trouvés")

# Récupérer la configuration du forfait
cursor.execute("SELECT valeur FROM configuration WHERE cle = 'forfait_courses'")
config_forfait = cursor.fetchone()
forfait_courses = int(config_forfait['valeur']) if config_forfait else 50

cursor.execute("SELECT valeur FROM configuration WHERE cle = 'prix_forfait'")
config_prix = cursor.fetchone()
prix_forfait = float(config_prix['valeur']) if config_prix else 1000

print(f"📦 Configuration : Forfait = {forfait_courses} courses, Prix = {prix_forfait} KMF")
print()

# Pour chaque conducteur, créer un abonnement s'il n'en a pas
for conducteur in conducteurs:
    conducteur_id = conducteur['id']
    immatricule = conducteur['immatricule']
    nom = conducteur['nom']
    
    cursor.execute('SELECT id FROM abonnements WHERE conducteur_id = ?', (conducteur_id,))
    abonnement = cursor.fetchone()
    
    if not abonnement:
        cursor.execute('''
            INSERT INTO abonnements 
            (conducteur_id, courses_achetees, courses_restantes, montant_paye, taxes_payees, statut)
            VALUES (?, ?, ?, ?, ?, 'actif')
        ''', (conducteur_id, forfait_courses, forfait_courses, prix_forfait, 0))
        print(f"✅ Abonnement créé pour {immatricule} ({nom}): {forfait_courses} courses")
    else:
        print(f"ℹ️ {immatricule} ({nom}) a déjà un abonnement")

conn.commit()

# Vérifier le résultat
cursor.execute('''
    SELECT COUNT(*) as count FROM abonnements
''')
count = cursor.fetchone()['count']
print(f"\n📊 {count} abonnements dans la base")

# Afficher le détail
cursor.execute('''
    SELECT c.immatricule, c.nom, a.courses_restantes, a.courses_achetees, a.statut
    FROM conducteurs c
    LEFT JOIN abonnements a ON c.id = a.conducteur_id
    WHERE c.compte_active = 1 OR c.compte_active IS NULL
''')
print("\n📋 ÉTAT DES ABONNEMENTS :")
for row in cursor.fetchall():
    immat = row['immatricule']
    nom = row['nom']
    rest = row['courses_restantes'] if row['courses_restantes'] is not None else '-'
    achet = row['courses_achetees'] if row['courses_achetees'] is not None else '-'
    statut = row['statut'] or 'AUCUN'
    print(f"   • {immat} ({nom}): {rest}/{achet} courses - {statut}")

conn.close()

print("\n" + "=" * 60)
print("✅ INITIALISATION TERMINÉE !")
print("=" * 60)