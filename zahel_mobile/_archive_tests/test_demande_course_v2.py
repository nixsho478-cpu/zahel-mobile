# test_demande_course_v2.py
import requests

token = "+26934011111"
data = {
    "depart": "Moroni Centre",
    "destination": "Université Comores",
    "prix": 65,
    "service": "confort"
}

headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

print(f"Token: {token}")
print(f"Data: {data}")

response = requests.post(
    "http://localhost:5001/api/courses/demander",
    json=data,
    headers=headers
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text}")