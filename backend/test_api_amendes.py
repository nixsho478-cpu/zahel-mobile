import requests
import json

print("🔍 TEST API AMENDES")
print("=" * 40)

url = 'http://localhost:5001/api/client/amendes'
headers = {'Authorization': '+26934011111'}

try:
    response = requests.get(url, headers=headers, timeout=5)
    print(f'✅ Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'📊 Amendes trouvées: {len(data.get("amendes", []))}')
        
        for i, amende in enumerate(data.get('amendes', [])):
            print(f'  {i+1}. {amende.get("raison")}: {amende.get("montant")} KMF')
    else:
        print(f'❌ Erreur: {response.text[:100]}')
        
except Exception as e:
    print(f'❌ Exception: {e}')