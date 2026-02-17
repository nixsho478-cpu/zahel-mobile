# test_direct_api.py
import requests
import json

base_url = "http://localhost:5001"

print("=== TEST DIRECT API ===")

# 1. Vérifier la course via l'API debug
print("\n1. Vérifier toutes les courses")
response = requests.get(f"{base_url}/api/debug/all_courses")
if response.status_code == 200:
    courses = response.json().get('courses', [])
    zahel_course = None
    
    for course in courses:
        if course.get('code_unique') == 'ZAHEL-AWN7383':
            zahel_course = course
            break
    
    if zahel_course:
        print(f"✅ Course ZAHEL-AWN7383 trouvée:")
        print(f"   Catégorie: {zahel_course.get('categorie_demande')}")
        print(f"   Statut: {zahel_course.get('statut')}")
        print(f"   Timer luxe: {zahel_course.get('timer_luxe_demarre_le')}")
        
        # Vérifier manuellement check_luxe
        print(f"\n2. Test manuel check_luxe")
        response = requests.get(f"{base_url}/api/courses/ZAHEL-AWN7383/check_luxe")
        print(f"   Status: {response.status_code}")
        print(f"   Réponse: {json.dumps(response.json(), indent=2)}")
    else:
        print("❌ Course ZAHEL-AWN7383 non trouvée dans l'API")
else:
    print(f"❌ Erreur API: {response.status_code}")