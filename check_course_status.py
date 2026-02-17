import sqlite3

def check_course_status():
    conn = sqlite3.connect('database/zahel_secure.db')
    cursor = conn.cursor()
    
    print("📊 ÉTAT DE LA COURSE ZAHEL-TQZ0246")
    print("=" * 50)
    
    # 1. Vérifier la course
    cursor.execute('''
        SELECT code_unique, statut, conducteur_id, prix_convenu, date_debut, date_fin
        FROM courses 
        WHERE code_unique = 'ZAHEL-TQZ0246'
    ''')
    
    course = cursor.fetchone()
    if course:
        code, statut, conducteur_id, prix, debut, fin = course
        print(f"Course: {code}")
        print(f"Statut: {statut}")
        print(f"Conducteur ID: {conducteur_id}")
        print(f"Prix: {prix} KMF")
        print(f"Début: {debut}")
        print(f"Fin: {fin}")
    else:
        print("❌ Course non trouvée")
        return
    
    # 2. Vérifier le conducteur
    cursor.execute('''
        SELECT immatricule, nom, en_course, disponible, courses_effectuees, gains_totaux
        FROM conducteurs 
        WHERE id = ?
    ''', (conducteur_id,))
    
    driver = cursor.fetchone()
    if driver:
        immatricule, nom, en_course, disponible, courses, gains = driver
        print(f"\n👤 Conducteur: {nom} ({immatricule})")
        print(f"En course: {'OUI' if en_course else 'NON'}")
        print(f"Disponible: {'OUI' if disponible else 'NON'}")
        print(f"Courses effectuées: {courses}")
        print(f"Gains totaux: {gains} KMF")
    
    # 3. Vérifier ce qui bloque
    print(f"\n🔍 DIAGNOSTIC:")
    
    if statut == 'terminee':
        print("❌ La course est DÉJÀ terminée!")
    elif statut != 'en_cours':
        print(f"❌ Course doit être 'en_cours' mais est '{statut}'")
        print("   Il faut d'abord commencer la course (/commencer)")
    elif en_course == 0:
        print("⚠️  Conducteur marqué comme 'pas en course'")
    else:
        print("✅ La course peut être terminée normalement")
    
    conn.close()

if __name__ == '__main__':
    check_course_status()