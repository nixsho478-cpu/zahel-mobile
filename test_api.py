import requests
import json

print("1. Recherche des courses disponibles...")
try:
    response = requests.get(
        'http://localhost:5001/api/courses/disponibles',
        headers={'Authorization': 'ZH-327KYM'},
        timeout=30
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        print(f"   Courses disponibles: {count}")
        
        if data.get('courses') and len(data['courses']) > 0:
            course = data['courses'][0]
            course_code = course['code']
            print(f"   Course sélectionnée: {course_code}")
            
            print(f"\n2. Test acceptation de {course_code}...")
            response2 = requests.post(
                f'http://localhost:5001/api/courses/{course_code}/accepter',
                headers={'Authorization': 'ZH-327KYM'},
                timeout=30
            )
            
            print(f"   Status: {response2.status_code}")
            if response2.status_code == 200:
                result = response2.json()
                print(f"   SUCCÈS: {result.get('message')}")
                print(f"   Course: {result.get('course')}")
            else:
                print(f"   Erreur: {response2.text[:100]}")
        else:
            print("   ℹ️ Aucune course disponible - créons-en une...")
            
            print("\n3. Création d'une course de test...")
            response3 = requests.post(
                'http://localhost:5001/api/courses/demander',
                headers={'Authorization': '+26934011111'},
                json={
                    'depart_lat': -11.700,
                    'depart_lng': 43.255,
                    'arrivee_lat': -11.710,
                    'arrivee_lng': 43.265,
                    'prix': 1800
                },
                timeout=5
            )
            
            print(f"   Status création: {response3.status_code}")
            if response3.status_code == 200:
                new_course = response3.json()['course']
                print(f"   ✅ Course créée: {new_course['code']}")
            else:
                print(f"   ❌ Erreur création: {response3.text[:100]}")
    
    else:
        print(f"   ❌ Erreur: {response.text[:100]}")
        
except Exception as e:
    print(f"💥 Exception: {e}")
    import traceback
    traceback.print_exc()