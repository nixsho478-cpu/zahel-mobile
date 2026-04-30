# migrate_abonnement_mensuel.py
import sqlite3
import os

db_path = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"

print("=" * 60)
print("🔄 MIGRATION VERS ABONNEMENT MENSUEL")
print("=" * 60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Sauvegarder les anciennes données
cursor.execute("SELECT conducteur_id, courses_restantes FROM abonnements")
anciens_abonnements = cursor.fetchall()
print(f"📦 {len(anciens_abonnements)} anciens abonnements trouvés")

# 2. Supprimer l'ancienne table
cursor.execute("DROP TABLE IF EXISTS abonnements")
print("🗑️ Ancienne table abonnements supprimée")

# 3. Créer la nouvelle table
cursor.execute('''
    CREATE TABLE abonnements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conducteur_id INTEGER NOT NULL UNIQUE,
        date_debut TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_expiration TIMESTAMP,
        montant_paye DECIMAL(10,2) DEFAULT 0,
        statut TEXT DEFAULT 'actif',  -- 'actif', 'expire', 'en_attente'
        courses_annulees INTEGER DEFAULT 0,
        mode_paiement TEXT,
        reference_paiement TEXT,
        date_paiement TIMESTAMP,
        confirme_par TEXT,
        notes TEXT,
        FOREIGN KEY (conducteur_id) REFERENCES conducteurs(id) ON DELETE CASCADE
    )
''')
print("✅ Nouvelle table abonnements créée")

# 4. Ajouter une colonne pour les annulations dans la table conducteurs (si pas déjà fait)
cursor.execute("PRAGMA table_info(conducteurs)")
colonnes = [col[1] for col in cursor.fetchall()]

if 'courses_annulees_mois' not in colonnes:
    cursor.execute('ALTER TABLE conducteurs ADD COLUMN courses_annulees_mois INTEGER DEFAULT 0')
    print("✅ Colonne courses_annulees_mois ajoutée")

# 5. Créer une table pour suivre les annulations
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
print("✅ Table annulations_conducteur créée")

# 6. Créer une table pour la configuration
cursor.execute('''
    CREATE TABLE IF NOT EXISTS configuration (
        cle TEXT PRIMARY KEY,
        valeur TEXT,
        modifiable INTEGER DEFAULT 1,
        description TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Insérer les configurations par défaut
config_defaut = [
    ('prix_abonnement_mensuel', '1000', 'Prix de l\'abonnement mensuel en KMF'),
    ('pourcentage_taxes', '5', 'Pourcentage de taxes ZAHEL sur chaque course'),
    ('whatsapp_agence', '2693608657', 'Numéro WhatsApp de l\'agence'),
    ('message_recu_abonnement', '✅ ZAHEL - Paiement confirmé !\n\nVotre abonnement mensuel de {montant} KMF a été reçu.\nValable jusqu\'au {date_expiration}.\n\nMerci de votre confiance !', 'Message de reçu WhatsApp')
]

for cle, valeur, desc in config_defaut:
    cursor.execute('''
        INSERT OR IGNORE INTO configuration (cle, valeur, description)
        VALUES (?, ?, ?)
    ''', (cle, valeur, desc))

print("✅ Configuration initialisée")

conn.commit()
conn.close()

print("\n" + "=" * 60)
print("✅ MIGRATION TERMINÉE AVEC SUCCÈS !")
print("=" * 60)