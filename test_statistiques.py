# test_statistiques.py - VERSION SIMPLIFIÉE
import requests
import json

print("=" * 70)
print("📊 TEST : STATISTIQUES PDG ZAHEL - VERSION SIMPLIFIÉE")
print("=" * 70)

# Token PDG
try:
    with open('token_pdg.txt', 'r') as f:
        token_pdg = f.read().strip()
except:
    token_pdg = "cad2ae6f475a86b35b3e4486d506b657f4b6b5653ade1dfeec434eae0bc77d5b"

print(f"🔑 Token PDG: {token_pdg[:20]}...")
print(f"🌐 URL: http://localhost:5001/api/admin/statistiques")

try:
    # Envoi de la requête
    print(f"\n📡 Envoi de la requête...")
    
    response = requests.get(
        "http://localhost:5001/api/admin/statistiques",
        headers={"Authorization": token_pdg},
        timeout=10
    )
    
    print(f"✅ Réponse reçue")
    print(f"   Statut HTTP: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success'):
            stats = data['statistiques']
            
            print("\n" + "🎯" * 30)
            print("🎯 DASHBOARD PDG ZAHEL - STATISTIQUES 🎯")
            print("🎯" * 30)
            
            # Section 1: Utilisateurs
            print("\n" + "👥" * 25)
            print("👥 UTILISATEURS ACTIFS")
            print("👥" * 25)
            print(f"├─ Conducteurs: {stats['conducteurs']['actifs']}/{stats['conducteurs']['total']} actifs")
            print(f"│  (Suspendus: {stats['conducteurs']['suspendus']})")
            print(f"└─ Clients: {stats['clients']['actifs']}/{stats['clients']['total']} actifs")
            print(f"   (Suspendus: {stats['clients']['suspendus']})")
            
            # Section 2: Courses
            print("\n" + "🚗" * 25)
            print("🚗 ACTIVITÉ DES COURSES")
            print("🚗" * 25)
            print(f"├─ Total courses: {stats['courses']['total']}")
            print(f"├─ Courses terminées: {stats['courses']['terminees']}")
            print(f"├─ Courses annulées: {stats['courses']['annulees']}")
            print(f"├─ Taux d'annulation: {stats['courses']['taux_annulation']}%")
            print(f"└─ Taux de complétion: {stats['courses']['taux_completion']}%")
            
            # Section 3: Finances
            print("\n" + "💰" * 25)
            print("💰 PERFORMANCE FINANCIÈRE")
            print("💰" * 25)
            print(f"├─ Revenus totaux: {stats['finances']['revenus_totaux']:,.2f} KMF")
            print(f"└─ Taxes collectées: {stats['finances']['taxes_totales']:,.2f} KMF")
            
            # Section 4: Calcul des indicateurs
            print("\n" + "📈" * 25)
            print("📈 INDICATEURS CLÉS")
            print("📈" * 25)
            
            if stats['conducteurs']['total'] > 0:
                productivite = stats['courses']['terminees'] / stats['conducteurs']['total'] if stats['conducteurs']['total'] > 0 else 0
                print(f"├─ Productivité: {productivite:.1f} courses/conducteur")
            
            if stats['courses']['terminees'] > 0:
                valeur_moyenne = stats['finances']['revenus_totaux'] / stats['courses']['terminees']
                print(f"├─ Valeur moyenne/course: {valeur_moyenne:,.0f} KMF")
            
            # Section 5: Message et timestamp
            print("\n" + "🔄" * 25)
            print("🔄 INFORMATIONS SYSTÈME")
            print("🔄" * 25)
            print(f"├─ Dernière mise à jour: {data['timestamp'][11:19]}")
            print(f"├─ Message: {data.get('message', 'Système opérationnel')}")
            print(f"└─ Source: {data.get('source', 'API ZAHEL')}")
            
            print("\n" + "✅" * 30)
            print("✅ DASHBOARD PDG FONCTIONNEL ! ✅")
            print("✅" * 30)
            print("\n📊 Vous pouvez maintenant voir les performances de ZAHEL en temps réel !")
            
        else:
            print(f"\n❌ Erreur dans la réponse: {data.get('error', 'Unknown error')}")
            print(f"   Message: {data.get('message', 'No message')}")
            
    elif response.status_code == 401:
        print("\n" + "🔒" * 25)
        print("🔒 ACCÈS REFUSÉ")
        print("🔒" * 25)
        print("├─ Token PDG invalide ou expiré")
        print("└─ Vérifiez votre token dans token_pdg.txt")
        
    elif response.status_code == 500:
        print("\n" + "💥" * 25)
        print("💥 ERREUR SERVEUR")
        print("💥" * 25)
        print(f"├─ Code: 500 (Internal Server Error)")
        print(f"└─ Détails: {response.text[:200]}...")
        
    else:
        print(f"\n⚠️  Réponse inattendue: {response.status_code}")
        print(f"   Contenu: {response.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print("\n" + "🔌" * 25)
    print("🔌 CONNEXION IMPOSSIBLE")
    print("🔌" * 25)
    print("├─ Le serveur ne répond pas")
    print("├─ Vérifiez que le serveur tourne:")
    print("│   1. Terminal 1: cd backend")
    print("│   2. Terminal 1: python api_zahel.py")
    print("└─ Puis réessayez")
    
except requests.exceptions.Timeout:
    print("\n⏰ La requête a expiré (timeout)")
    print("  Le serveur met trop de temps à répondre")
    
except Exception as e:
    print(f"\n💥 Erreur inattendue: {e}")
    print(f"  Type: {type(e).__name__}")

print("\n" + "=" * 70)
print("💡 ASTUCE: Pour rafraîchir les stats, relancez ce script")
print("=" * 70)

# Attente pour voir les résultats
input("\nAppuyez sur ENTREE pour terminer...")