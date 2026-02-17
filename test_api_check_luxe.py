# test_api_check_luxe.py
import requests
import json

# Récupérer le dernier code de course
import sqlite3
conn = sqlite3.connect(r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db")
cursor = conn.cursor()
cursor.execute("SELECT code_unique FROM courses ORDER BY id DESC LIMIT 1")
last_course = cursor.fetchone()[0]
conn.close()

print(f"🔍 TEST API CHECK LUXE POUR : {last_course}")
print("=" * 60)

# Appeler l'API
url = f"http://localhost:5001/api/courses/{last_course}/check_luxe"
headers = {
    'Authorization': '+26934011111',
    'Content-Type': 'application/json'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"📡 URL: {url}")
    print(f"📡 Status: {response.status_code}")
    print(f"📡 Response: {response.text}")
    
    data = response.json()
    print(f"\n📊 ANALYSE :")
    print(f"   Success: {data.get('success')}")
    print(f"   is_luxe: {data.get('is_luxe')}")
    print(f"   message: {data.get('message')}")
    
    # Vérifier les données détaillées
    if 'data' in data:
        print(f"\n📈 DATA :")
        for key, value in data['data'].items():
            print(f"   {key}: {value}")
            
except Exception as e:
    print(f"❌ Erreur: {e}")