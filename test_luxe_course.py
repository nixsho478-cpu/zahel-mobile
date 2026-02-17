# test_luxe_course.py
import requests
import json

API_BASE = "http://localhost:5001"

def test_luxe_course():
    # 1. Créer une course luxe
    print("=== CRÉATION COURSE LUXE ===")
    data = {
        'depart_lat': -11.6980,
        'depart_lng': 43.2560,
        'arrivee_lat': -11.7100,
        'arrivee_lng': 43.2650,
        'prix': 2700,
        'service': 'luxe'  # <-- IMPORTANT
    }
    
    response = requests.post(f"{API_BASE}/api/courses/demander", json=data)
    result = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        course_code = result['course']['code']
        
        # 2. Vérifier avec check_luxe
        print(f"\n=== VÉRIFICATION TIMER LUXE ===")
        response = requests.get(f"{API_BASE}/api/courses/{course_code}/check_luxe")
        result = response.json()
        print(f"Check luxe: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    test_luxe_course()