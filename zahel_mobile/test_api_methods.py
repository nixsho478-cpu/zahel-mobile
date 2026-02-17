# test_api_methods.py
import sys
sys.path.append('.')

from api.client import APIClient

client = APIClient()

print("=== Test des méthodes ===")
print(f"Méthode demander_course: {hasattr(client, 'demander_course')}")

# Vérifier les paramètres attendus
import inspect
if hasattr(client, 'demander_course'):
    sig = inspect.signature(client.demander_course)
    print(f"Signature: {sig}")
    print(f"Paramètres: {list(sig.parameters.keys())}")