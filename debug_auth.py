# debug_auth.py
import requests
import sqlite3

print("🔍 DEBUG AUTHENTIFICATION COMPLÈTE")
print("="*50)

# Utilise le token qui marche pour GET /
token = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"
print(f"Token utilisé : {token[:20]}...")

# 1. Test GET / (marche)
print("\n1. GET / (doit marcher) :")
r = requests.get("http://localhost:5001",
                 headers={"Authorization": token})
print(f"   Status : {r.status_code}")

# 2. Test POST /api/courses/demander (ne marche pas)
print("\n2. POST /api/courses/demander (problème) :")
data = {
    "depart_lat": -11.698,
    "depart_lng": 43.256,
    "arrivee_lat": -11.704,
    "arrivee_lng": 43.261,
    "prix": 1500
}

r = requests.post("http://localhost:5001/api/courses/demander",
                  headers={"Authorization": token},
                  json=data)
print(f"   Status : {r.status_code}")
print(f"   Error  : {r.text[:200]}")

# 3. Vérifier dans la base quel type d'utilisateur c'est
print("\n3. Vérification base de données :")

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Chercher l'utilisateur avec ce hash
cursor.execute("""
    SELECT telephone, nom, password_hash
    FROM clients
    WHERE password_hash = ?
""", (token,))
client = cursor.fetchone()

if client:
    print(f"   ✅ Client trouvé : {client[0]} – {client[1]}")
else:
    print(f"   ❌ Aucun client avec ce hash !")

# Chercher dans conducteurs
cursor.execute("""
    SELECT immatricule, nom, password_hash
    FROM conducteurs
    WHERE password_hash = ?
""", (token,))
conducteur = cursor.fetchone()

if conducteur:
    print(f"   🚗 C'est un conducteur : {conducteur[0]} – {conducteur[1]}")

conn.close()
print("\n" + "="*50)
input("Appuyez sur Entrée pour continuer...")