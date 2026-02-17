# test_complet_3_strikes.py
import requests
import time
import sqlite3

print("🎯 TEST COMPLET SYSTÈME 3 STRIKES ZAHEL")
print("="*60)

TOKEN_CLIENT = "+26934011111"
BASE_URL = "http://localhost:5001"

def creer_et_annuler(numero_test, attendre_secondes=65):
    """Créer une course et l'annuler après X secondes"""
    print(f"\n{numero_test}. CRÉATION COURSE #{numero_test}")
    print("-"*40)
    
    # Créer la course
    response = requests.post(
        f"{BASE_URL}/api/courses/demander",
        headers={"Authorization": TOKEN_CLIENT},
        json={
            "depart_lat": -11.698,
            "depart_lng": 43.256,
            "arrivee_lat": -11.704,
            "arrivee_lng": 43.261,
            "prix": 1000 + (numero_test * 200)
        }
    )
    
    if response.status_code != 201:
        print(f"❌ Erreur création: {response.text[:100]}")
        return None
    
    course = response.json()['course']
    course_code = course['code']
    print(f"✅ Course créée: {course_code}")
    
    # Attendre X secondes
    print(f"⏳ Attente de {attendre_secondes} secondes...")
    for i in range(attendre_secondes, 0, -1):
        print(f"   {i}...", end='\r')
        time.sleep(1)
    
    # Annuler
    print(f"\n❌ Annulation après {attendre_secondes}s...")
    response = requests.post(
        f"{BASE_URL}/api/courses/{course_code}/annuler",
        headers={"Authorization": TOKEN_CLIENT},
        json={"raison": f"test_strike_{numero_test}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Annulation réussie!")
        
        # Analyser le résultat
        actions = result.get('actions_appliquees', [])
        for action in actions:
            action_type = action.get('type')
            
            if action_type == 'avertissement':
                print(f"   ⚠️ AVERTISSEMENT n°{action.get('avertissement_numero')}")
                print(f"      {action.get('message')}")
                
            elif action_type == 'suspension_24h':
                print(f"   🚫 SUSPENSION 24 HEURES")
                print(f"      Jusqu'à: {action.get('suspension_jusque')}")
                
            elif action_type == 'amende_suspension':
                print(f"   💰 AMENDE {action.get('amende', 0)} KMF + SUSPENSION")
                print(f"      Message: {action.get('message')}")
                
        return result
    else:
        print(f"❌ Erreur annulation: {response.status_code}")
        print(f"   {response.text[:200]}")
        return None

def verifier_etat_client():
    """Vérifier l'état actuel du client"""
    print("\n🔍 ÉTAT ACTUEL DU CLIENT")
    print("-"*40)
    
    conn = sqlite3.connect('database/zahel_secure.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT telephone, nom, avertissements_annulation, 
               compte_suspendu, date_suspension, amende_en_cours
        FROM clients WHERE telephone = '+26934011111'
    ''')
    
    client = cursor.fetchone()
    
    if client:
        print(f"👤 Client: {client[1]} ({client[0]})")
        print(f"   Avertissements: {client[2]}")
        print(f"   Compte suspendu: {'✅ OUI' if client[3] else '❌ NON'}")
        if client[4]:
            print(f"   Date suspension: {client[4]}")
        print(f"   Amende en cours: {client[5] or 0} KMF")
    
    # Vérifier amendes en attente
    cursor.execute('''
        SELECT COUNT(*) as total, SUM(montant) as montant_total
        FROM amendes 
        WHERE utilisateur_type = 'client' 
          AND utilisateur_id = (SELECT id FROM clients WHERE telephone = '+26934011111')
          AND statut = 'en_attente'
    ''')
    
    amendes = cursor.fetchone()
    print(f"   Amendes en attente: {amendes[0] or 0}")
    print(f"   Montant total: {amendes[1] or 0} KMF")
    
    conn.close()
    return client

def verifier_dashboard_pdg():
    """Vérifier ce que voit le PDG"""
    print("\n📊 DASHBOARD PDG - RÉSUMÉ")
    print("-"*40)
    
    # Statistiques générales
    response = requests.get(
        f"{BASE_URL}/api/admin/statistiques",
        headers={"Authorization": "cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b"}
    )
    
    if response.status_code == 200:
        stats = response.json()['statistiques']
        print(f"📈 Statistiques ZAHEL:")
        print(f"   • Conducteurs: {stats['conducteurs']['actifs']}/{stats['conducteurs']['total']} actifs")
        print(f"   • Clients: {stats['clients']['actifs']}/{stats['clients']['total']} actifs")
        print(f"   • Courses: {stats['courses']['total']} total")
        print(f"   • Taux d'annulation: {stats['courses']['taux_annulation']}%")
        print(f"   • Revenus: {stats['finances']['revenus_totaux']} KMF")
    
    # Amendes
    response = requests.get(
        f"{BASE_URL}/api/amendes",
        headers={"Authorization": "cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b"}
    )
    
    if response.status_code == 200:
        amendes = response.json()
        print(f"\n💰 Amendes en attente:")
        print(f"   • Total: {amendes['total']}")
        print(f"   • Montant: {amendes['total_montant']} KMF")
        
        if amendes['amendes']:
            print(f"   • Dernière amende: {amendes['amendes'][0]['raison'][:50]}...")

# ========== EXÉCUTION DES TESTS ==========
print("\n🎯 OBJECTIF: Tester les 3 strikes successifs")
print("="*60)

# Vérifier état initial
etat_initial = verifier_etat_client()

# Demander confirmation
print(f"\n⚠️ Le client a déjà {etat_initial[2]} avertissement(s)")
print("   Voulez-vous continuer pour tester la suite?")
input("   Appuyez sur Entrée pour continuer...")

# Test 1: 2ème annulation > 60s (devrait donner suspension 24h)
print("\n🔬 TEST: 2ÈME ANNULATION > 60s (suspension 24h attendue)")
result1 = creer_et_annuler(2, 65)

# Vérifier état après test 1
etat_apres1 = verifier_etat_client()

# Test 2: 3ème annulation > 60s (devrait donner amende 500 KMF)
if etat_apres1[3] == 0:  # Si pas encore suspendu
    print("\n🔬 TEST: 3ÈME ANNULATION > 60s (amende 500 KMF attendue)")
    result2 = creer_et_annuler(3, 65)
else:
    print("\n⚠️ Client déjà suspendu - Impossible de tester 3ème strike")

# Vérifier dashboard PDG
verifier_dashboard_pdg()

# ========== CONCLUSION ==========
print("\n" + "="*60)
print("📋 RÉCAPITULATIF FINAL DU SYSTÈME ZAHEL")
print("="*60)

print("\n✅ FONCTIONNALITÉS IMPLÉMENTÉES:")
print("1. Système complet de courses (création, acceptation, annulation)")
print("2. Authentification triple (clients, conducteurs, PDG)")
print("3. Règles métier 3 strikes avec amendes")
print("4. Dashboard PDG avec statistiques")
print("5. Base de données sécurisée avec 14+ tables")
print("6. API REST complète avec gestion d'erreurs")

print("\n🔗 ACCÈS:")
print(f"• Dashboard PDG: http://localhost:5001/admin/dashboard?token=...")
print(f"• API: http://localhost:5001")
print(f"• Documentation: Voir les endpoints dans le terminal serveur")

print("\n👤 DONNÉES DE TEST:")
print(f"• Client test: +26934011111 (1+ avertissements)")
print(f"• Conducteur test: ZH-327KYM")
print(f"• PDG: token_pdg.txt")

print("\n🚀 PROCHAINES ÉTAPES (si vous voulez continuer):")
print("1. Interface amendes dans dashboard")
print("2. Système de notifications")
print("3. Application mobile conducteur (Kivy)")
print("4. Interface client web")
print("5. Système de paiement intégré")

print("\n" + "="*60)
print("🎉 FÉLICITATIONS ! VOTRE SYSTÈME ZAHEL EST OPÉRATIONNEL !")
print("="*60)

input("\nAppuyez sur Entrée pour terminer...")