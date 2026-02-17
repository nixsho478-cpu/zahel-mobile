print("=" * 40)
print("TEST ZAHEL - ÉTAPE 1")
print("=" * 40)
print()

print("✅ Étape 1 : Python fonctionne")
import sys
print(f"   Version : {sys.version}")
print()

print("✅ Étape 2 : Packages installés")
try:
    import flask
    print("   Flask : OK")
except:
    print("   Flask : PAS INSTALLÉ")

try:
    import requests
    print("   Requests : OK")
except:
    print("   Requests : PAS INSTALLÉ")
print()

print("=" * 40)
print("TEST TERMINÉ - TOUT EST BON !")
print("=" * 40)

input("\nAppuie sur ENTREE pour continuer...")