# test_terminer.py
import requests
import json

print("=" * 60)
print("🏁 TEST : TERMINER UNE COURSE - CYCLE COMPLET")
print("=" * 60)

# Informations
code_course = "ZAHEL-XKX6475"  # La course qu'on a commencée
token_conducteur = "ZH-327KYM"  # Le même conducteur

print(f"📋 Course à terminer : {code_course}")
print(f"👤 Conducteur       : {token_conducteur}")
print(f"🎯 Objectif         : Compléter le cycle d'une course")

try:
    # 1. Terminer la course
    print(f"\n1. 🏁 Arrivée à destination...")
    
    url = f"http://localhost:5001/api/courses/{code_course}/terminer"
    headers = {"Authorization": token_conducteur}
    
    response = requests.post(url, headers=headers, timeout=10)
    
    print(f"\n✅ RÉPONSE REÇUE")
    print(f"   Statut : {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        finances = result['course']['finances']
        
        print(f"\n🎉🎉🎉 CYCLE COMPLET RÉUSSI ! 🎉🎉🎉")
        print("=" * 50)
        print(f"COURSE : {result['course']['code']}")
        print(f"STATUT : {result['course']['statut']}")
        print(f"DÉBUT  : {result['course']['debut'][11:19]}")
        print(f"FIN    : {result['course']['fin'][11:19]}")
        print("-" * 50)
        print("💰 FINANCES :")
        print(f"  Prix convenu   : {finances['prix_convenu']} KMF")
        print(f"  Prix final     : {finances['prix_final']} KMF")
        print(f"  Taxes ZAHEL    : {finances['taxes_zahel']} KMF ({finances['pourcentage_taxes']}%)")
        print(f"  Gain conducteur: {finances['gain_conducteur']} KMF")
        print("=" * 50)
        
        print(f"\n📊 RÉCAPITULATIF DU CYCLE :")
        print("  1. ✅ Course créée (en_attente)")
        print("  2. ✅ Course acceptée (acceptee)")
        print("  3. ✅ Course commencée (en_cours)")
        print("  4. ✅ COURSE TERMINÉE (terminee) ← NOUVEAU !")
        
        print(f"\n🎯 MISSION ACCOMPLIE : Le système de courses ZAHEL est FONCTIONNEL !")
        
    elif response.status_code == 400:
        print(f"\n⚠️  Erreur : {response.json().get('error', 'Course non en cours')}")
        print("   Vérifie le statut de la course")
        
    else:
        print(f"\n⚠️  Autre erreur : {response.text}")
        
except Exception as e:
    print(f"\n💥 Erreur : {e}")

print("\n" + "=" * 60)
input("Appuie sur ENTREE pour voir le récapitulatif complet...")