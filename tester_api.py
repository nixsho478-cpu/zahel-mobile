# tester_api.py
import requests
import json
import time

print("🧪 TEST DE L'API ZAHEL AVEC CATÉGORIES")
print("=" * 50)

def test_api():
    try:
        # 1. Test connexion conducteur
        print("\n1. 🔐 CONNEXION CONDUCTEUR ZH-641NZZ")
        print("-" * 40)
        
        response = requests.post(
            'http://localhost:5001/api/conducteur/login',
            json={'immatricule': 'ZH-641NZZ', 'password': 'zahel123'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if not response.ok:
            print(f"❌ Échec connexion: {response.text}")
            return False
        
        data = response.json()
        token = data.get('token')
        print(f"✅ Token: {token}")
        
        # 2. Test courses disponibles
        print("\n2. 📋 COURSES DISPONIBLES AVEC FILTRE CATÉGORIE")
        print("-" * 40)
        
        headers = {'Authorization': token}
        response2 = requests.get(
            'http://localhost:5001/api/courses/disponibles',
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response2.status_code}")
        
        if not response2.ok:
            print(f"❌ Erreur courses: {response2.text}")
            return False
        
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
        
        # Afficher quelques courses
        courses = data2.get('courses', [])
        if courses:
            print(f"\n3. 🚗 COURSES TROUVÉES ({len(courses)} max)")
            print("-" * 40)
            
            for i, course in enumerate(courses[:5]):  # 5 premières
                categorie = course.get('categorie', 'standard')
                code = course.get('code', 'N/A')
                prix = course.get('prix_convenu', 0)
                
                print(f"  {i+1}. {code}")
                print(f"     Catégorie: {categorie}")
                print(f"     Prix: {prix} KMF")
                print(f"     Statut: {course.get('statut')}")
                print()
        else:
            print("ℹ️  Aucune course disponible")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ API non démarrée ou inaccessible")
        print("💡 Lance d'abord l'API avec: python api_zahel.py")
        return False
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Attendre 2 secondes pour laisser l'API démarrer si besoin
    time.sleep(2)
    test_api()