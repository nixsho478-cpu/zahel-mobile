# test_demande_course.py
import requests

token = "+26934011111"
data = {
    "depart": "Moroni Centre",
    "destination": "Université Comores",
    "prix": 65,
    "service": "confort",
    "client_token": token
}

response = requests.post("http://localhost:5001/api/courses/demander", json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")