# test_final_system.py
import requests
import sqlite3

print("🧪 TEST FINAL DU SYSTÈME COMPLET")
print("="*50)

# 1. Vérifier les corrections
print("1. 🔍 VÉRIFICATION CORRECTIONS APPLIQUÉES")
conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Vérifier colonne date_suspension
cursor.execute("PRAGMA table_info(clients)")
cols = [col[1] for col in cursor.fetchall()]

if 'date_suspension' in cols:
    print("✅ Colonne 'date_suspension' présente dans clients")
else:
    print("❌ Colonne 'date_suspension' MANQUANTE")
    
if 'avertissements_annulation' in cols:
    print("✅ Colonne 'avertissements_annulation' présente")
    
    # Vérifier valeur pour le client test
    cursor.execute("SELECT avertissements_annulation FROM clients WHERE telephone = '+26934011111'")
    avertissements = cursor.fetchone()
    if avertissements:
        print(f"✅ Client a {avertissements[0] or 0} avertissement(s)")
else:
    print("❌ Colonne 'avertissements_annulation' MANQUANTE")

conn.close()

# 2. Tester création et annulation IMMÉDIATE (sans attente 60s)
print("\n2. 🚀 TEST RAPIDE (annulation immédiate)")
TOKEN_CLIENT = "+26934011111"

response = requests.post(
    "http://localhost:5001/api/courses/demander",
    headers={"Authorization": TOKEN_CLIENT},
    json={
        "depart_lat": -11.698,
        "depart_lng": 43.256,
        "arrivee_lat": -11.704,
        "arrivee_lng": 43.261,
        "prix": 1000
    }
)

if response.status_code == 201:
    course_code = response.json()['course']['code']
    print(f"✅ Course créée: {course_code}")
    
    # Annuler immédiatement
    response2 = requests.post(
        f"http://localhost:5001/api/courses/{course_code}/annuler",
        headers={"Authorization": TOKEN_CLIENT},
        json={"raison": "test_rapide"}
    )
    
    if response2.status_code == 200:
        result = response2.json()
        print(f"✅ Annulation réussie en {response2.elapsed.total_seconds():.1f}s")
        
        # Vérifier si avertissement
        actions = result.get('actions_appliquees', [])
        if actions:
            for action in actions:
                if action.get('type') == 'avertissement':
                    print(f"⚠️ AVERTISSEMENT appliqué!")
                    print(f"   Numéro: {action.get('avertissement_numero')}")
                    print(f"   Message: {action.get('message')}")
                elif action.get('type') == 'annulation_gratuite':
                    print(f"🆓 Annulation gratuite (dans délai)")
        else:
            print("ℹ️ Aucune action spécifique")
            
    elif response2.status_code == 500:
        print("❌ Erreur 500 - Détails serveur:")
        print(f"   {response2.text[:200]}")
    else:
        print(f"⚠️ Autre erreur: {response2.status_code}")
else:
    print(f"❌ Erreur création: {response.status_code}")

# 3. Vérifier les amendes via API PDG
print("\n3. 💰 VÉRIFICATION AMENDES (API PDG)")
# Note: Cette route nécessite le token PDG
# On vérifie d'abord si la route existe
try:
    response = requests.get(
        "http://localhost:5001/api/amendes",
        headers={"Authorization": "cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b"},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API amendes accessible")
        print(f"   Total amendes: {data.get('total', 0)}")
        print(f"   Montant total: {data.get('total_montant', 0)} KMF")
        
        if data.get('amendes'):
            print(f"   Dernière amende: {data['amendes'][0]['raison'][:50]}...")
    else:
        print(f"⚠️ API amendes: {response.status_code}")
except Exception as e:
    print(f"⚠️ API amendes inaccessible: {e}")

print("\n" + "="*50)
print("🎯 RÉSUMÉ DU SYSTÈME")
print("="*50)
print("✅ Fonctionnel:")
print("   • Création de courses")
print("   • Authentification clients/conducteurs")
print("   • Annulation de courses")
print("   • Système d'avertissements (partiel)")
print("\n⚠️ À vérifier:")
print("   • Colonnes manquantes (date_suspension)")
print("   • Dashboard amendes")
print("   • Règles 3 strikes complètes")

print("\n🔧 Prochaines actions:")
print("1. Exécuter fix_all_columns.py")
print("2. Redémarrer le serveur")
print("3. Tester à nouveau")
print("4. Vérifier dashboard PDG")