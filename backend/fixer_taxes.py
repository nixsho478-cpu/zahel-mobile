# fixer_taxes.py
import sqlite3
import os

print("🔧 CORRECTION DES TAXES ZAHEL")
print("=" * 50)

# Chemin de la base de données
db_path = "database/zahel_secure.db"

if not os.path.exists(db_path):
    print(f"❌ ERREUR: Base de données non trouvée: {db_path}")
    input("Appuyez sur ENTREE pour quitter...")
    exit()

try:
    # Connexion à la base
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📊 Étape 1: Vérification des données actuelles...")
    
    # Voir les courses terminées
    cursor.execute("SELECT code_unique, prix_convenu, taxes_zahel FROM courses WHERE statut = 'terminee'")
    courses = cursor.fetchall()
    
    if not courses:
        print("❌ Aucune course terminée trouvée")
    else:
        print(f"✅ {len(courses)} course(s) terminée(s) trouvée(s)")
        
        for course in courses:
            print(f"   • {course[0]}: {course[1]} KMF, Taxes: {course[2]} KMF")
    
    print("\n📊 Étape 2: Calcul des taxes manquantes...")
    
    # Calculer ce que devraient être les taxes (5% du prix)
    cursor.execute("""
        SELECT SUM(prix_convenu * 0.05) 
        FROM courses 
        WHERE statut = 'terminee' AND (taxes_zahel IS NULL OR taxes_zahel = 0)
    """)
    taxes_calculees = cursor.fetchone()[0] or 0
    
    print(f"   Taxes à ajouter: {taxes_calculees} KMF")
    
    print("\n📊 Étape 3: Mise à jour des taxes...")
    
    # Mettre à jour les taxes
    cursor.execute("""
        UPDATE courses 
        SET taxes_zahel = prix_convenu * 0.05 
        WHERE statut = 'terminee' AND (taxes_zahel IS NULL OR taxes_zahel = 0)
    """)
    
    rows_updated = cursor.rowcount
    print(f"   ✅ {rows_updated} course(s) mise(s) à jour")
    
    print("\n📊 Étape 4: Mise à jour des statistiques...")
    
    # Calculer le total des taxes
    cursor.execute("SELECT SUM(taxes_zahel) FROM courses WHERE statut = 'terminee'")
    total_taxes = cursor.fetchone()[0] or 0
    
    # Mettre à jour la table statistiques
    cursor.execute("""
        UPDATE statistiques 
        SET taxes_dues = ?
        WHERE id = 1
    """, (total_taxes,))
    
    print(f"   ✅ Taxes totales dans statistiques: {total_taxes} KMF")
    
    # Valider les changements
    conn.commit()
    
    print("\n📊 Étape 5: Vérification finale...")
    
    # Vérifier après correction
    cursor.execute("SELECT code_unique, prix_convenu, taxes_zahel FROM courses WHERE statut = 'terminee'")
    courses_corrigees = cursor.fetchall()
    
    print("   Courses après correction:")
    for course in courses_corrigees:
        pourcentage = (course[2] / course[1] * 100) if course[1] > 0 else 0
        print(f"   • {course[0]}: {course[1]} KMF → Taxes: {course[2]} KMF ({pourcentage:.1f}%)")
    
    # Vérifier les statistiques
    cursor.execute("SELECT taxes_dues FROM statistiques WHERE id = 1")
    stats_taxes = cursor.fetchone()[0] or 0
    print(f"   📈 Taxes dans statistiques: {stats_taxes} KMF")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("🎉 CORRECTION TERMINÉE AVEC SUCCÈS !")
    print("=" * 50)
    print("\n🔄 Maintenant, rafraîchissez votre dashboard PDG (F5)")
    print("   Les taxes devraient apparaître: 60 KMF au lieu de 0 KMF")
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    print("   Vérifiez que la base de données n'est pas utilisée par le serveur")

print("\n" + "-" * 50)
input("Appuyez sur ENTREE pour fermer...")