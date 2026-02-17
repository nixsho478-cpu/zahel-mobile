# test_session_complet.py
import json
import time
import os

print("🔧 TEST COMPLET DU SYSTÈME DE SESSION")

# 1. Créer un fichier session valide
test_session = {
    'user_type': 'client',
    'identifier': '+26934011111',
    'token': '+26934011111',
    'timestamp': time.time()  # Maintenant
}

with open('session.json', 'w') as f:
    json.dump(test_session, f, indent=2)

print("✅ session.json créé avec données valides")

# 2. Vérifier le contenu
with open('session.json', 'r') as f:
    data = json.load(f)
    print(f"📋 Contenu: {data}")

# 3. Vérifier l'expiration (ne devrait pas être expiré)
age = time.time() - data['timestamp']
print(f"⏰ Âge de la session: {age:.0f} secondes")
print(f"📱 Session expirée? {age > 604800}")