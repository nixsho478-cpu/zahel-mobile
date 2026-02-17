# verifier_dashboard.py
import requests
import json

print('🔍 VÉRIFICATION DU DASHBOARD AMENDES')
print('='*60)

TOKEN_PDG = "cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b"

# 1. Vérifier les amendes via API
print('1. 📋 LISTE DES AMENDES :')
try:
    response = requests.get(
        'http://localhost:5001/api/amendes',
        headers={'Authorization': TOKEN_PDG},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f'   ✅ {data["total"]} amende(s) trouvée(s)')
        print(f'   💰 Total montant : {data["total_montant"]} KMF')
        
        for amende in data['amendes']:
            print(f'      • #{amende["id"]} : {amende["nom_utilisateur"]} - {amende["montant"]} KMF - {amende["statut"]}')
    else:
        print(f'   ❌ Erreur API: {response.status_code}')
        
except Exception as e:
    print(f'   ❌ Erreur connexion: {e}')

# 2. Vérifier les statistiques
print('\n2. 📊 STATISTIQUES :')
try:
    response = requests.get(
        'http://localhost:5001/api/admin/statistiques',
        headers={'Authorization': TOKEN_PDG},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        stats = data['statistiques']['finances']
        print(f'   ✅ Statistiques disponibles')
        print(f'      • Amendes dues   : {stats.get("amendes_dues", 0)} KMF')
        print(f'      • Amendes payées : {stats.get("amendes_payees", 0)} KMF')
    else:
        print(f'   ❌ Erreur API: {response.status_code}')
        
except Exception as e:
    print(f'   ❌ Erreur connexion: {e}')

# 3. Tester le paiement d'une amende
print('\n3. 🧪 TEST PAIEMENT (simulation) :')
try:
    # Trouver une amende en attente
    response = requests.get(
        'http://localhost:5001/api/amendes?statut=en_attente',
        headers={'Authorization': TOKEN_PDG},
        timeout=5
    )
    
    if response.status_code == 200:
        amendes = response.json()['amendes']
        if amendes:
            amende_id = amendes[0]['id']
            print(f'   Amende disponible pour test: #{amende_id}')
            print('   (Le paiement peut être testé depuis l\'interface dashboard)')
        else:
            print('   Aucune amende en attente')
    else:
        print(f'   ❌ Erreur: {response.status_code}')
        
except Exception as e:
    print(f'   ❌ Erreur: {e}')

print('\n' + '='*60)
print('🎯 POUR TESTER LE DASHBOARD :')
print('1. Accédez à : http://localhost:5001/admin/dashboard?token=...')
print('2. Vérifiez la section "GESTION DES AMENDES EN ATTENTE"')
print('3. Cliquez sur "Amendes en attente"')
print('4. Testez les boutons "Marquer payée" et "Annuler"')
print('='*60)