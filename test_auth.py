import sqlite3

def test_conducteur_in_db():
    """Vérifier ce qui est dans la base de données"""
    
    print("🔍 INSPECTION BASE DE DONNÉES")
    print("=" * 50)
    
    conn = sqlite3.connect('database/zahel_secure.db')
    cursor = conn.cursor()
    
    # 1. Voir TOUS les conducteurs
    cursor.execute('SELECT id, immatricule, nom, courses_effectuees, gains_totaux, disponible FROM conducteurs')
    conducteurs = cursor.fetchall()
    
    print("📋 TOUS LES CONDUCTEURS:")
    for c in conducteurs:
        print(f"   ID:{c[0]} | {c[1]} | {c[2]} | Courses:{c[3]} | Gains:{c[4]} | Disp:{c[5]}")
    
    # 2. Vérifier spécifiquement ZH-327KYM
    print(f"\n🔍 CONDUCTEUR ZH-327KYM:")
    cursor.execute('''
        SELECT id, immatricule, nom, telephone, 
               courses_effectuees, gains_totaux, 
               disponible, en_course,
               compte_suspendu, compte_active
        FROM conducteurs 
        WHERE immatricule = 'ZH-327KYM'
    ''')
    
    driver = cursor.fetchone()
    if driver:
        print(f"✅ Trouvé!")
        print(f"   ID: {driver[0]}")
        print(f"   Immatricule: {driver[1]}")
        print(f"   Nom: {driver[2]}")
        print(f"   Téléphone: {driver[3]}")
        print(f"   Courses effectuées: {driver[4]}")
        print(f"   Gains totaux: {driver[5]} KMF")
        print(f"   Disponible: {'OUI' if driver[6] else 'NON'}")
        print(f"   En course: {'OUI' if driver[7] else 'NON'}")
        print(f"   Suspendu: {'OUI' if driver[8] else 'NON'}")
        print(f"   Actif: {'OUI' if driver[9] else 'NON'}")
    else:
        print("❌ Non trouvé!")
    
    # 3. Vérifier s'il y a un token_auth
    print(f"\n🔍 COLONNES DE LA TABLE conducteurs:")
    cursor.execute('PRAGMA table_info(conducteurs)')
    columns = cursor.fetchall()
    for col in columns:
        print(f"   {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == '__main__':
    test_conducteur_in_db()