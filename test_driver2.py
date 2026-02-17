# Test du conducteur et de l'API
import sqlite3
import requests
import json

print("=== VÉRIFICATION BASE DE DONNÉES ===")
conn = sqlite3.connect("database/zahel_secure.db")
cursor = conn.cursor()

# Vérifier ZH-327KYM
cursor.execute("SELECT immatricule, nom, disponible, en_course, latitude, longitude FROM conducteurs WHERE immatricule='ZH-327KYM'")
driver = cursor.fetchone()

if driver:
    print(f"• Immatricule: {driver[0]}")
    print(f"• Nom: {driver[1]}")
    print(f"• Disponible: {driver[2]} (1=OUI)")
    print(f"• En course: {driver[3]} (0=NON)")
    print(f"• Position GPS: {driver[4]}, {driver[5]}")
else:
    print("❌ Conducteur ZH-327KYM introuvable!")

print()
print("=== TOUS LES CONDUCTEURS DISPONIBLES ===")
cursor.execute("SELECT immatricule, nom, disponible FROM conducteurs WHERE disponible=1")
available = cursor.fetchall()
print(f"Nombre: {len(available)}")
for d in available:
    print(f"  • {d[0]}: {d[1]}")

conn.close()

print()
print("=== TEST API DIRECT ===")
url = "http://localhost:5001/api/conducteurs/disponibles"
params = {
    "lat": -11.6957,
    "lng": 43.2560,
    "radius": 10
}

try:
    response = requests.get(url, params=params, timeout=5)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Success: {data.get('success')}")
    print(f"Count: {data.get('count', 0)}")
    
    if data.get("conducteurs"):
        for d in data["conducteurs"]:
            print(f"  • {d.get('immatricule')}: {d.get('nom')}")
    else:
        print("  ❌ Liste vide")
except Exception as e:
    print(f"❌ Erreur API: {e}")
