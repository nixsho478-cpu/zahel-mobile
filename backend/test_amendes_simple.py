# test_amendes_simple.py
import requests

url = 'http://localhost:5001/api/client/amendes'
headers = {'Authorization': '+26934011111'}

try:
    response = requests.get(url, headers=headers, timeout=5)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:500]}')  # Premier 500 caractères
except Exception as e:
    print(f'Exception: {e}')