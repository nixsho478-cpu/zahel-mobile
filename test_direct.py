import requests
import json

# Test direct de l'API
response = requests.get(
    "http://localhost:5001/api/conducteur/statistiques",
    headers={"Authorization": "ZH-327KYM"}
)

print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Body: {response.text}")

# Essayer de parser le JSON
try:
    data = response.json()
    print(f"\nParsed JSON:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
except:
    print("\n❌ Impossible de parser le JSON")