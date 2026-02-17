# corriger_taxes.py
import sqlite3

print("=" * 50)
print("💰 CORRECTION DES TAXES ZAHEL")
print("=" * 50)

# Chemin correct
chemin_bd = "database/zahel_secure.db"

try:
    # Connexion
    conn = sqlite3.connect(chemin_bd)
    cursor = conn.cursor()
    
    print("📊 1. Calcul des taxes manquantes...")
    
    # Voir ce qu'il y a actuellement
    cursor.execute("SELECT code_unique, prix_convenu, taxes_zahel FROM courses WHERE statut = 'terminee'")
    courses = cursor.fetchall()
    
    for course in courses:
        print(f"   • {course[0]}: {course[1]} KMF, Taxes actuelles: {course[2]} KMF")
    
    print("\n📊 2. Application des taxes (5%)...")
    
    # Appliquer 5% de taxes
    cursor.execute("""
        UPDATE courses 
        SET taxes_zahel = ROUND(prix_convenu * 0.05, 2)
        WHERE statut = 'terminee'
    """)
    
    print(f"   ✅ {cursor.rowcount} course(s) corrigée(s)")
    
    print("\n📊 3. Calcul du total des taxes...")
    
    cursor.execute("SELECT SUM(taxes_zahel) FROM courses WHERE statut = 'terminee'")
    total = cursor.fetchone()[0] or 0
    print(f"   💰 Total taxes: {total} KMF")
    
    print("\n📊 4. Mise à jour des statistiques...")
    
    cursor.execute("UPDATE statistiques SET taxes_dues = ? WHERE id = 1", (total,))
    print(f"   📈 Statistiques mises à jour")
    
    # Sauvegarder
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print("🎉 CORRECTION RÉUSSIE !")
    print("=" * 50)
    print("\n➡️  Actions à faire maintenant:")
    print("   1. Retournez sur votre dashboard PDG")
    print("   2. Appuyez sur F5 (Rafraîchir)")
    print("   3. Les taxes devraient être à 60 KMF")
    print("=" * 50)
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")

print()
input("Appuyez sur ENTREE pour terminer...")