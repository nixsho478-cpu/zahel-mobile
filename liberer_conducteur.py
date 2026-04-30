# liberer_conducteur.py
import sqlite3
import os

print("=" * 60)
print("🔓 LIBÉRATION DU CONDUCTEUR")
print("=" * 60)

# Chemin vers la base de données
db_path = r"C:\Users\USER\Desktop\zahel\backend\zahel_secure.db"

# Vérifier que le fichier existe
if not os.path.exists(db_path):
    print(f"❌ Base de données non trouvée: {db_path}")
    print("   Recherche d'autres emplacements...")
    
    # Autres emplacements possibles
    alternatives = [
        r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db",
        r"C:\Users\USER\Desktop\zahel\zahel_secure.db"
    ]
    
    for alt in alternatives:
        if os.path.exists(alt):
            db_path = alt
            print(f"✅ Trouvée: {db_path}")
            break
    else:
        print("❌ Aucune base de données trouvée")
        exit(1)

try:
    # Connexion à la base
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n📂 Base de données: {db_path}")
    print("-" * 60)
    
    # 1. Voir l'état actuel
    print("\n🔍 ÉTAT ACTUEL:")
    
    cursor.execute("SELECT immatricule, en_course, disponible FROM conducteurs")
    conducteurs = cursor.fetchall()
    
    for immatricule, en_course, disponible in conducteurs:
        statut = "🟢 DISPONIBLE" if disponible and not en_course else "🔴 OCCUPÉ"
        if en_course:
            statut = "🚗 EN COURSE"
        elif not disponible:
            statut = "⏸️ INDISPONIBLE"
        print(f"   {immatricule}: {statut}")
    
    # 2. Voir les courses en cours
    cursor.execute("""
        SELECT code_unique, statut, conducteur_id 
        FROM courses 
        WHERE statut IN ('en_cours', 'acceptee')
    """)
    courses = cursor.fetchall()
    
    print("\n🚗 COURSES EN COURS:")
    if courses:
        for code, statut, cond_id in courses:
            print(f"   {code}: {statut} (conducteur_id: {cond_id})")
    else:
        print("   Aucune course en cours")
    
    # 3. Libérer le conducteur ZH-952XKW
    print("\n🔓 LIBÉRATION...")
    
    # Récupérer l'ID du conducteur
    cursor.execute("SELECT id FROM conducteurs WHERE immatricule = 'ZH-952XKW'")
    result = cursor.fetchone()
    
    if result:
        conducteur_id = result[0]
        print(f"✅ Conducteur trouvé: ID {conducteur_id}")
        
        # Libérer le conducteur
        cursor.execute("UPDATE conducteurs SET en_course = 0, disponible = 1 WHERE id = ?", (conducteur_id,))
        print(f"✅ Conducteur libéré: en_course=0, disponible=1")
        
        # Libérer ses courses
        cursor.execute("""
            UPDATE courses 
            SET statut = 'en_recherche', conducteur_id = NULL 
            WHERE conducteur_id = ? AND statut != 'terminee'
        """, (conducteur_id,))
        print(f"✅ Courses libérées: {cursor.rowcount} course(s) remise(s) en recherche")
        
        conn.commit()
    else:
        print("❌ Conducteur ZH-952XKW non trouvé")
    
    # 4. Vérification finale
    print("\n✅ VÉRIFICATION FINALE:")
    
    cursor.execute("SELECT immatricule, en_course, disponible FROM conducteurs")
    conducteurs = cursor.fetchall()
    
    for immatricule, en_course, disponible in conducteurs:
        if immatricule == 'ZH-952XKW':
            print(f"   {immatricule}: en_course={en_course}, disponible={disponible} ✅")
        else:
            print(f"   {immatricule}: en_course={en_course}, disponible={disponible}")
    
    cursor.execute("SELECT COUNT(*) FROM courses WHERE statut IN ('en_cours', 'acceptee')")
    courses_encours = cursor.fetchone()[0]
    print(f"\n📊 Courses en cours après libération: {courses_encours}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ OPÉRATION TERMINÉE - Le conducteur est libéré !")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()