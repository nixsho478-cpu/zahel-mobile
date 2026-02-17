# test_filtre_moto.py
import requests
import json

print("🧪 TEST FILTRAGE - CONDUCTEUR MOTO (ZH-641NZZ)")
print("=" * 60)

def test_conducteur_moto():
    try:
        # 1. Connexion ZH-641NZZ (moto)
        print("\n1. 🔐 CONNEXION ZH-641NZZ (catégorie: moto)")
        print("-" * 40)
        
        response = requests.post(
            'http://localhost:5001/api/conducteur/login',
            json={'immatricule': 'ZH-641NZZ', 'password': 'test123'},
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
        print("\n2. 📋 COURSES DISPONIBLES POUR MOTO")
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
            print(f"\n3. 🚗 COURSES VISIBLES (devraient être uniquement 'moto')")
            print("-" * 40)
            
            courses_par_categorie = {}
            for course in courses:
                categorie = course.get('categorie', 'standard')
                courses_par_categorie[categorie] = courses_par_categorie.get(categorie, 0) + 1
            
            for cat, nb in courses_par_categorie.items():
                print(f"   • {cat}: {nb} course(s)")
            
            print(f"\n4. 📝 DÉTAIL DES COURSES")
            print("-" * 40)
            for i, course in enumerate(courses[:3]):  # 3 premières
                print(f"   {i+1}. {course.get('code')}")
                print(f"      Catégorie: {course.get('categorie')}")
                print(f"      Prix: {course.get('prix_convenu')} KMF")
                print(f"      Statut: {course.get('statut')}")
                print()
                
            # Vérification
            if 'confort' in courses_par_categorie:
                print("⚠️  ATTENTION: Le conducteur 'moto' voit des courses 'confort' !")
                print("   C'est une erreur de filtre.")
            else:
                print("✅ CORRECT: Le conducteur 'moto' ne voit que les courses 'moto'")
                
        else:
            print("ℹ️  Aucune course disponible pour cette catégorie")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conducteur_moto()