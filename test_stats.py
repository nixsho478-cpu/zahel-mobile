#!/usr/bin/env python3
# test_stats.py - TEST CORRIGÉ

import requests
import json

def test_conducteur_stats():
    """Tester les statistiques du conducteur - VERSION CORRIGÉE"""
    
    print("📊 TEST DES STATISTIQUES CONDUCTEUR")
    print("=" * 50)
    
    # Appeler l'API des statistiques
    response = requests.get(
        "http://localhost:5001/api/conducteur/statistiques",
        headers={"Authorization": "ZH-327KYM"}
    )
    
    print(f"✅ Réponse API: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # ⭐⭐ AFFICHER LE JSON COMPLET POUR DEBUG ⭐⭐
        print("\n📦 JSON COMPLET:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get('success'):
            conducteur = data['conducteur']
            perf = conducteur.get('performance', {})
            statut = conducteur.get('statut', {})
            
            print(f"\n📈 STATISTIQUES DE {conducteur.get('immatricule', 'N/A')}:")
            print(f"   Courses effectuées: {perf.get('courses_effectuees', 0)}")
            print(f"   Gains totaux: {perf.get('gains_totaux', 0):,.0f} KMF")
            print(f"   Note moyenne: {perf.get('note_moyenne', 5.0)}")
            print(f"   Disponible: {'OUI' if statut.get('disponible') else 'NON'}")
            print(f"   En course: {'OUI' if statut.get('en_course') else 'NON'}")
            print(f"   Courses ce mois: {perf.get('courses_ce_mois', 0)}")
            print(f"   Gains ce mois: {perf.get('gains_ce_mois', 0):,.0f} KMF")
        else:
            print(f"❌ Erreur dans la réponse: {data.get('error')}")
    else:
        print(f"❌ HTTP Erreur: {response.status_code}")
        print(f"   Réponse: {response.text[:200]}")

if __name__ == '__main__':
    test_conducteur_stats()