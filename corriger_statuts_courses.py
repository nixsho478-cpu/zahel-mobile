# corriger_statuts_courses.py
import sqlite3
import os

def corriger_statuts_courses():
    """Corriger les statuts des courses de 'en_recherche' à 'en_attente'"""
    
    # Chemin vers la base de données
    db_path = os.path.join('database', 'zahel_secure.db')
    
    try:
        # Connexion à la base
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Vérifier combien de courses ont le statut 'en_recherche'
        cursor.execute("""
            SELECT COUNT(*) FROM courses 
            WHERE statut = 'en_recherche'
        """)
        count = cursor.fetchone()[0]
        
        print(f"📊 Courses avec statut 'en_recherche': {count}")
        
        if count == 0:
            print("✅ Aucune course à corriger")
            return
        
        # 2. Afficher les courses à corriger
        cursor.execute("""
            SELECT code_unique, statut, conducteur_id 
            FROM courses 
            WHERE statut = 'en_recherche'
            LIMIT 10
        """)
        
        courses = cursor.fetchall()
        print("\n📋 Courses à corriger (10 premières):")
        for course in courses:
            print(f"  - {course[0]} : {course[1]} (conducteur: {course[2]})")
        
        # 3. Demander confirmation
        print(f"\n⚠️  Voulez-vous corriger {count} course(s) ?")
        print("   Les statuts 'en_recherche' deviendront 'en_attente'")
        
        reponse = input("   Tapez 'OUI' pour confirmer: ").strip().upper()
        
        if reponse == 'OUI':
            # 4. Effectuer la correction
            cursor.execute("""
                UPDATE courses 
                SET statut = 'en_attente' 
                WHERE statut = 'en_recherche'
            """)
            
            rows_updated = cursor.rowcount
            conn.commit()
            
            print(f"\n✅ MISE À JOUR EFFECTUÉE !")
            print(f"   {rows_updated} course(s) corrigée(s)")
            
            # 5. Vérification
            cursor.execute("""
                SELECT COUNT(*) FROM courses 
                WHERE statut = 'en_recherche'
            """)
            count_apres = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM courses 
                WHERE statut = 'en_attente'
            """)
            count_en_attente = cursor.fetchone()[0]
            
            print(f"\n📊 STATISTIQUES APRÈS CORRECTION:")
            print(f"   Courses 'en_recherche': {count_apres}")
            print(f"   Courses 'en_attente': {count_en_attente}")
            
        else:
            print("\n❌ Correction annulée")
        
        # 6. Afficher aussi les autres statuts pour info
        cursor.execute("""
            SELECT statut, COUNT(*) 
            FROM courses 
            GROUP BY statut
            ORDER BY statut
        """)
        
        print("\n📊 RÉPARTITION DES STATUTS:")
        for statut, nb in cursor.fetchall():
            print(f"   {statut}: {nb} course(s)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")

if __name__ == '__main__':
    print("=" * 50)
    print("🔧 CORRECTEUR DE STATUTS DES COURSES ZAHEL")
    print("=" * 50)
    corriger_statuts_courses()
    print("\n" + "=" * 50)
    input("Appuyez sur Entrée pour quitter...")