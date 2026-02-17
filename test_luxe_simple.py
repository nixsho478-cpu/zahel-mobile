# test_luxe_simple.py
import requests
import json
import time

print("🔍 TEST MANUEL TIMEOUT LUXE")

try:
    # 1. Connexion
    response = requests.post(
        'http://localhost:5001/api/client/login',
        json={'telephone': '+26934011111', 'password': 'test123'},
        timeout=10
    )
    
    if not response.ok:
        print('❌ Erreur connexion')
        exit()
    
    token = response.json().get('token')
    print(f'✅ Token: {token}')
    
    # 2. Créer course luxe
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    course_data = {
        'depart_lat': -11.698,
        'depart_lng': 43.256,
        'arrivee_lat': -11.720,
        'arrivee_lng': 43.270,
        'prix': 4500.0,
        'categorie': 'luxe'
    }
    
    response2 = requests.post(
        'http://localhost:5001/api/courses/demander',
        headers=headers,
        json=course_data,
        timeout=10
    )
    
    if not response2.ok:
        print(f'❌ Erreur création: {response2.text}')
        exit()
    
    course_code = response2.json().get('course', {}).get('code')
    print(f'✅ Course luxe créée: {course_code}')
    
    # 3. Vérifier plusieurs fois
    for i in range(5):
        time.sleep(2)
        
        response3 = requests.get(
            f'http://localhost:5001/api/courses/{course_code}/check_luxe',
            timeout=10
        )
        
        if response3.ok:
            data = response3.json()
            print(f'Vérification {i+1}:')
            print(f'  Timeout: {data.get("timeout")}')
            print(f'  Temps écoulé: {data.get("temps_ecoule", 0)}s')
            msg = data.get("message", "")[:50]
            print(f'  Message: {msg}...')
            print()
        else:
            print(f'❌ Erreur vérification: {response3.text}')
            
except Exception as e:
    print(f'❌ Erreur générale: {e}')