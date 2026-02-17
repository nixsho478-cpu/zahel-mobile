# test_post.py
import requests

response = requests.post(
    "http://localhost:5001/api/courses/demander",
    headers={"Authorization": "+26934011111"},  # Notez: pas d'espace avant Authorization
    json={
        "depart_lat": -11.698,
        "depart_lng": 43.256,
        "arrivee_lat": -11.704,
        "arrivee_lng": 43.261,
        "prix": 1000
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")