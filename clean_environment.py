# clean_environment.py
import sqlite3
import datetime

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

print("🧹 NETTOYAGE DE L'ENVIRONNEMENT ZAHEL")
print("=" * 50)

# 1. Compter avant
cursor.execute("SELECT statut, COUNT(*) FROM courses GROUP BY statut")
print("\n📊 STATUT DES COURSES AVANT:")
for statut, count in cursor.fetchall():
    print(f"   {statut}: {count}")

# 2. Mettre toutes les courses en_attente à terminée
cursor.execute("""
    UPDATE courses 
    SET statut = 'terminee',
        conducteur_id = COALESCE(conducteur_id, 1),
        date_fin = datetime('now'),
        prix_final = prix_convenu
    WHERE statut = 'en_attente'
""")
courses_cleaned = cursor.rowcount

# 3. Réinitialiser le conducteur test
cursor.execute("""
    UPDATE conducteurs 
    SET disponible = 1,
        en_course = 0,
        latitude = -11.698,
        longitude = 43.256
    WHERE immatricule = 'ZH-327KYM'
""")

# 4. Créer une nouvelle course test propre
test_code = 'ZAHEL-TEST-' + datetime.datetime.now().strftime('%H%M%S')
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

cursor.execute("""
    INSERT INTO courses (
        code_unique, client_id, conducteur_id,
        point_depart_lat, point_depart_lng, 
        point_arrivee_lat, point_arrivee_lng,
        prix_convenu, statut, date_demande
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    test_code, 3, None,
    -11.698, 43.256,  # Centre Ville
    -11.710, 43.265,  # Destination test
    200, 'en_attente', now
))

# 5. Marquer les amendes du client comme payées (pour tests propres)
cursor.execute("""
    UPDATE amendes 
    SET statut = 'payee',
        date_paiement = datetime('now')
    WHERE utilisateur_id = 3 AND utilisateur_type = 'client'
""")
amendes_cleaned = cursor.rowcount

conn.commit()

# 6. Afficher le résultat
cursor.execute("SELECT statut, COUNT(*) FROM courses GROUP BY statut")
print("\n📊 STATUT DES COURSES APRÈS:")
for statut, count in cursor.fetchall():
    print(f"   {statut}: {count}")

print(f"\n✅ RÉSULTAT DU NETTOYAGE:")
print(f"   • {courses_cleaned} courses nettoyées")
print(f"   • Conducteur ZH-327KYM réinitialisé")
print(f"   • {amendes_cleaned} amendes marquées payées")
print(f"   • Nouvelle course créée: {test_code}")
print(f"   • Prix: 200 KMF, Statut: en_attente")

# Vérification finale
cursor.execute("""
    SELECT code_unique, statut, conducteur_id, prix_convenu
    FROM courses 
    WHERE statut = 'en_attente'
""")
print("\n🎯 COURSES DISPONIBLES APRÈS NETTOYAGE:")
for code, statut, conducteur, prix in cursor.fetchall():
    print(f"   • {code}: {prix} KMF, Conducteur: {'AUCUN' if conducteur is None else 'ATTRIBUÉ'}")

conn.close()