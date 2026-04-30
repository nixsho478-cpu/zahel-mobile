# migrate_abonnement_v2.py
import sqlite3
import os

db_path = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"

print("=" * 60)
print("🔄 MIGRATION V2 - ABONNEMENT PAR FORFAIT DE COURSES")
print("=" * 60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Supprimer l'ancienne table
cursor.execute("DROP TABLE IF EXISTS abonnements")
print("🗑️ Ancienne table abonnements supprimée")

# 2. Créer la nouvelle table (version forfait)
cursor.execute('''
    CREATE TABLE abonnements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conducteur_id INTEGER NOT NULL UNIQUE,
        courses_achetees INTEGER DEFAULT 50,
        courses_restantes INTEGER DEFAULT 50,
        date_achat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_expiration TIMESTAMP,
        montant_paye DECIMAL(10,2) DEFAULT 0,
        taxes_payees DECIMAL(10,2) DEFAULT 0,
        statut TEXT DEFAULT 'actif',
        mode_paiement TEXT,
        reference_paiement TEXT,
        confirme_par TEXT,
        notes TEXT,
        FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id) ON DELETE CASCADE
    )
''')
print("✅ Nouvelle table abonnements créée (version forfait)")

# 3. Créer la table de configuration si elle n'existe pas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS configuration (
        cle TEXT PRIMARY KEY,
        valeur TEXT,
        modifiable INTEGER DEFAULT 1,
        description TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 4. Insérer/mettre à jour les configurations
config_defaut = [
    ('forfait_courses', '50', 'Nombre de courses par forfait'),
    ('prix_forfait', '1000', 'Prix du forfait en KMF'),
    ('pourcentage_taxes', '5', 'Pourcentage de taxes ZAHEL sur chaque course'),
    ('whatsapp_agence', '2693608657', 'Numéro WhatsApp de l\'agence'),
    ('message_recu_abonnement', '✅ ZAHEL - Paiement confirmé !\n\nForfait {courses} courses: {montant} KMF\nTaxes payées: {taxes} KMF\nTotal: {total} KMF\n\nCourses restantes: {courses}\nMerci de votre confiance !', 'Message de reçu WhatsApp')
]

for cle, valeur, desc in config_defaut:
    cursor.execute('''
        INSERT OR REPLACE INTO configuration (cle, valeur, description)
        VALUES (?, ?, ?)
    ''', (cle, valeur, desc))

print("✅ Configuration initialisée/mise à jour")

# 5. Ajouter la colonne courses_annulees_mois si elle n'existe pas
cursor.execute("PRAGMA table_info(conducteurs)")
colonnes = [col[1] for col in cursor.fetchall()]
if 'courses_annulees_mois' not in colonnes:
    cursor.execute('ALTER TABLE conducteurs ADD COLUMN courses_annulees_mois INTEGER DEFAULT 0')
    print("✅ Colonne courses_annulees_mois ajoutée")

# 6. Créer la table des annulations
cursor.execute('''
    CREATE TABLE IF NOT EXISTS annulations_conducteur (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conducteur_id INTEGER NOT NULL,
        course_code TEXT NOT NULL,
        raison TEXT,
        date_annulation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id)
    )
''')
print("✅ Table annulations_conducteur vérifiée")

conn.commit()
conn.close()

print("\n" + "=" * 60)
print("✅ MIGRATION V2 TERMINÉE AVEC SUCCÈS !")
print("=" * 60)
print("\n📋 CONFIGURATION PAR DÉFAUT :")
print("   • Forfait : 50 courses")
print("   • Prix forfait : 1000 KMF")
print("   • Taxes : 5% par course")