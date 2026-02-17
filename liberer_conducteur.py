# liberer_conducteur.py
import sqlite3
import datetime

print("=" * 50)
print("🔧 LIBÉRATION DU CONDUCTEUR ZH-327KYM")
print("=" * 50)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# 1. Trouver le conducteur
cursor.execute('SELECT id, nom FROM conducteurs WHERE immatricule = "ZH-327KYM"')
conducteur = cursor.fetchone()

if not conducteur:
    print("❌ Conducteur ZH-327KYM non trouvé")
    exit()

conducteur_id, nom = conducteur
print(f"✅ Conducteur trouvé: {nom} (ID: {conducteur_id})")

# 2. Vérifier son état actuel
cursor.execute('SELECT disponible, en_course FROM conducteurs WHERE id = ?', (conducteur_id,))
disponible, en_course = cursor.fetchone()
print(f"📊 État actuel:")
print(f"  • Disponible: {'❌ NON' if disponible == 0 else '✅ OUI'}")
print(f"  • En course: {'❌ OUI' if en_course == 1 else '✅ NON'}")

# 3. Terminer les courses en cours
cursor.execute('''
    SELECT id, code_unique, statut 
    FROM courses 
    WHERE conducteur_id = ? 
    AND statut IN ('en_cours', 'acceptee')
''', (conducteur_id,))

courses = cursor.fetchall()
print(f"\n📦 Courses à traiter: {len(courses)}")

if courses:
    for course_id, code, statut in courses:
        print(f"  • {code} - {statut}")
        
        if statut == 'en_cours':
            # Terminer la course
            maintenant = datetime.datetime.now().isoformat()
            cursor.execute('''
                UPDATE courses 
                SET statut = 'terminee',
                    date_fin = ?,
                    paiement_effectue = 1
                WHERE id = ?
            ''', (maintenant, course_id))
            print(f"    ✅ Course terminée")
        elif statut == 'acceptee':
            # Annuler l'acceptation
            cursor.execute('''
                UPDATE courses 
                SET statut = 'en_attente',
                    conducteur_id = NULL,
                    date_acceptation = NULL
                WHERE id = ?
            ''', (course_id,))
            print(f"    ✅ Acceptation annulée, course remise en attente")

# 4. Libérer le conducteur
cursor.execute('''
    UPDATE conducteurs 
    SET disponible = 1,
        en_course = 0,
        updated_at = ?
    WHERE id = ?
''', (datetime.datetime.now().isoformat(), conducteur_id))

print(f"\n🔄 Conducteur libéré:")
print(f"  • Disponible: ✅ OUI")
print(f"  • En course: ✅ NON")

# 5. Vérifier
cursor.execute('SELECT disponible, en_course FROM conducteurs WHERE id = ?', (conducteur_id,))
disponible, en_course = cursor.fetchone()
print(f"\n📋 VÉRIFICATION:")
print(f"  • Disponible: {'✅ OUI' if disponible == 1 else '❌ NON'}")
print(f"  • En course: {'❌ OUI' if en_course == 1 else '✅ NON'}")

conn.commit()
conn.close()

print("\n" + "=" * 50)
print("🎯 Conducteur ZH-327KYM est maintenant DISPONIBLE !")
print("   Relancez l'app Kivy pour voir les courses.")
input("Appuyez sur ENTREE pour continuer...")