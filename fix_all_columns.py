# fix_all_columns.py
import sqlite3

print("🔧 CORRECTION COMPLÈTE DE TOUTES LES TABLES")
print("="*50)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# === TABLE CLIENTS ===
print("\n📋 TABLE CLIENTS")
cursor.execute("PRAGMA table_info(clients)")
client_cols = [col[1] for col in cursor.fetchall()]
print(f"Colonnes existantes ({len(client_cols)}): {', '.join(client_cols)}")

# Colonnes nécessaires pour le système d'amendes
client_required = [
    ('date_suspension', 'DATETIME'),
    ('suspension_jusque', 'DATETIME'),
    ('motif_suspension', 'TEXT'),
    ('avertissements_annulation', 'INTEGER DEFAULT 0'),
    ('amende_en_cours', 'REAL DEFAULT 0'),
    ('courses_gratuites', 'INTEGER DEFAULT 0')
]

for col_name, col_type in client_required:
    if col_name not in client_cols:
        try:
            cursor.execute(f"ALTER TABLE clients ADD COLUMN {col_name} {col_type}")
            print(f"✅ Ajoutée: {col_name} ({col_type})")
        except Exception as e:
            print(f"⚠️ Erreur {col_name}: {e}")
    else:
        print(f"✅ Déjà présente: {col_name}")

# === TABLE CONDUCTEURS ===
print("\n🚗 TABLE CONDUCTEURS")
cursor.execute("PRAGMA table_info(conducteurs)")
cond_cols = [col[1] for col in cursor.fetchall()]
print(f"Colonnes existantes ({len(cond_cols)}): {', '.join(cond_cols[:10])}...")

cond_required = [
    ('courses_gratuites', 'INTEGER DEFAULT 0'),
    ('date_suspension', 'DATETIME'),
    ('motif_suspension', 'TEXT')
]

for col_name, col_type in cond_required:
    if col_name not in cond_cols:
        try:
            cursor.execute(f"ALTER TABLE conducteurs ADD COLUMN {col_name} {col_type}")
            print(f"✅ Ajoutée: {col_name} ({col_type})")
        except Exception as e:
            print(f"⚠️ Erreur {col_name}: {e}")
    else:
        print(f"✅ Déjà présente: {col_name}")

# === TABLE AMENDES ===
print("\n💰 TABLE AMENDES")
cursor.execute("PRAGMA table_info(amendes)")
amende_cols = [col[1] for col in cursor.fetchall()]
print(f"Colonnes existantes ({len(amende_cols)}): {', '.join(amende_cols)}")

# Vérifier les données existantes
cursor.execute("SELECT COUNT(*) FROM amendes")
amende_count = cursor.fetchone()[0]
print(f"📊 Amendes enregistrées: {amende_count}")

if amende_count > 0:
    cursor.execute("SELECT id, utilisateur_type, montant, raison, statut FROM amendes LIMIT 5")
    amendes = cursor.fetchall()
    print("📋 Dernières amendes:")
    for amende in amendes:
        print(f"  ID {amende[0]}: {amende[1]} - {amende[2]} KMF - {amende[3]} - {amende[4]}")

# === TABLE STATISTIQUES ===
print("\n📊 TABLE STATISTIQUES")
try:
    cursor.execute("PRAGMA table_info(statistiques)")
    stat_cols = [col[1] for col in cursor.fetchall()]
    print(f"Colonnes existantes ({len(stat_cols)}):")
    for col in stat_cols:
        print(f"  - {col}")
except:
    print("⚠️ Table statistiques non trouvée")

conn.commit()
conn.close()

print("\n✅ CORRECTIONS TERMINÉES !")
print("\n🔧 Actions nécessaires:")
print("1. Redémarrer le serveur Flask")
print("2. Tester à nouveau l'annulation")
print("3. Vérifier le dashboard PDG")