# test_filtre_confort.py
import requests
import json

print("🧪 TEST FILTRAGE - CONDUCTEUR CONFORT (ZH-327KYM)")
print("=" * 60)

def test_conducteur_confort():
    try:
        # 1. Connexion ZH-327KYM (confort)
        print("\n1. 🔐 CONNEXION ZH-327KYM (catégorie: confort)")
        print("-" * 40)
        
        response = requests.post(
            'http://localhost:5001/api/conducteur/login',
            json={'immatricule': 'ZH-327KYM', 'password': 'test123'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if not response.ok:
            print(f"❌ Échec: {response.text}")
            return
        
        data = response.json()
        token = data.get('token')
        conducteur_nom = data.get('conducteur', {}).get('nom')
        print(f"✅ Connecté: {conducteur_nom}")
        print(f"✅ Token: {token}")
        
        # 2. Voir les courses disponibles
        print("\n2. 📋 COURSES DISPONIBLES POUR CONFORT")
        print("-" * 40)
        
        headers = {'Authorization': token}
        response2 = requests.get(
            'http://localhost:5001/api/courses/disponibles',
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response2.status_code}")
        
        if not response2.ok:
            print(f"❌ Erreur: {response2.text}")
            return
        
        data2 = response2.json()
        success = data2.get('success', False)
        count = data2.get('count', 0)
        
        print(f"✅ Success: {success}")
        print(f"✅ Nombre de courses: {count}")
        
        # Informations sur le filtre
        filtre = data2.get('filtre_categorie', {})
        if filtre:
            print(f"✅ Conducteur catégorie: {filtre.get('conducteur')}")
            print(f"✅ Catégories visibles: {filtre.get('categories_visibles')}")
        
        # Analyser les courses
        courses = data2.get('courses', [])
        if courses:
            print(f"\n3. 🚗 COURSES VISIBLES (devraient être 'standard' + 'confort')")
            print("-" * 40)
            
            courses_par_categorie = {}
            for course in courses:
                categorie = course.get('categorie', 'standard')
                courses_par_categorie[categorie] = courses_par_categorie.get(categorie, 0) + 1
            
            for cat, nb in courses_par_categorie.items():
                print(f"   • {cat}: {nb} course(s)")
            
            # Chercher notre course "confort" spécifique
            print(f"\n4. 🔍 RECHERCHE DE LA COURSE 'confort' ZAHEL-VEK9456")
            print("-" * 40)
            
            course_trouvee = False
            for course in courses:
                if course.get('code') == 'ZAHEL-VEK9456':
                    course_trouvee = True
                    print(f"   ✅ TROUVÉE !")
                    print(f"      Code: {course.get('code')}")
                    print(f"      Catégorie: {course.get('categorie')}")
                    print(f"      Prix: {course.get('prix_convenu')} KMF")
                    break
            
            if not course_trouvee:
                print("   ❌ NON TROUVÉE - Problème de filtre !")
            
            # Vérification
            visible_categories = list(courses_par_categorie.keys())
            expected_categories = ['standard', 'confort']
            
            print(f"\n5. ✅ VÉRIFICATION HIÉRARCHIE")
            print("-" * 40)
            print(f"   Catégories visibles: {visible_categories}")
            print(f"   Catégories attendues: {expected_categories}")
            
            if set(visible_categories).issubset(set(expected_categories)):
                print("   ✅ CORRECT: Le conducteur 'confort' voit uniquement 'standard' + 'confort'")
            else:
                print("   ⚠️  ATTENTION: Catégories inattendues visibles")
                
        else:
            print("ℹ️  Aucune course disponible pour cette catégorie")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conducteur_confort()