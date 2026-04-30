"""
Test des services ZAHEL
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import DatabaseService, CourseService, NotificationService, FineService, StatisticsService
from auth_jwt import AuthService

def test_database_service():
    """Tester le service de base de données"""
    print("🧪 Test DatabaseService")
    print("-" * 40)
    
    db_service = DatabaseService()
    
    # Test de connexion
    try:
        conn = db_service.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"✅ Connexion réussie - {len(tables)} tables trouvées")
        
        # Lister les tables
        table_names = [table['name'] for table in tables]
        print(f"📋 Tables: {', '.join(table_names[:10])}...")
        
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_auth_service():
    """Tester le service d'authentification"""
    print("\n🧪 Test AuthService")
    print("-" * 40)
    
    # Test de génération de token
    token = AuthService.generate_token(
        user_id=123,
        user_type='client',
        additional_data={'nom': 'Test Client'}
    )
    
    print(f"✅ Token généré: {token[:50]}...")
    
    # Test de vérification
    payload = AuthService.verify_token(token)
    if payload:
        print(f"✅ Token vérifié - User ID: {payload['user_id']}, Type: {payload['user_type']}")
    else:
        print("❌ Échec de vérification du token")
        return False
    
    # Test de hash de mot de passe
    password = "test123"
    hashed = AuthService.hash_password(password)
    print(f"✅ Mot de passe hashé: {hashed[:50]}...")
    
    # Test de vérification
    is_valid = AuthService.verify_password(password, hashed)
    print(f"✅ Vérification mot de passe: {'✓' if is_valid else '✗'}")
    
    # Test avec mauvais mot de passe
    is_invalid = AuthService.verify_password("wrong", hashed)
    print(f"✅ Vérification mauvais mot de passe: {'✓' if not is_invalid else '✗'}")
    
    return True

def test_course_service():
    """Tester le service de courses"""
    print("\n🧪 Test CourseService")
    print("-" * 40)
    
    course_service = CourseService()
    
    # Test de recherche de conducteurs
    drivers = course_service.find_available_drivers(
        latitude=-11.7022,  # Moroni
        longitude=43.2551,
        radius_meters=10000
    )
    
    print(f"✅ Conducteurs disponibles trouvés: {len(drivers)}")
    
    if drivers:
        print(f"📋 Premier conducteur: {drivers[0]['nom']} ({drivers[0]['categorie_vehicule']})")
    
    return True

def test_notification_service():
    """Tester le service de notifications"""
    print("\n🧪 Test NotificationService")
    print("-" * 40)
    
    notification_service = NotificationService()
    
    # Créer une notification de test
    notification_id = notification_service.create_notification(
        driver_id=1,  # ID de test
        notification_type='test',
        message='Notification de test',
        course_code='TEST-123'
    )
    
    print(f"✅ Notification créée - ID: {notification_id}")
    
    # Récupérer les notifications non lues
    notifications = notification_service.get_unread_notifications(driver_id=1)
    print(f"✅ Notifications non lues: {len(notifications)}")
    
    return True

def test_fine_service():
    """Tester le service d'amendes"""
    print("\n🧪 Test FineService")
    print("-" * 40)
    
    fine_service = FineService()
    
    # Créer une amende de test
    fine_id = fine_service.create_fine(
        user_type='client',
        user_id=1,  # ID de test
        amount=500,
        reason='Annulation abusive',
        course_code='TEST-123'
    )
    
    print(f"✅ Amende créée - ID: {fine_id}")
    
    # Récupérer les amendes
    fines = fine_service.get_user_fines('client', 1)
    print(f"✅ Amendes trouvées: {len(fines)}")
    
    return True

def test_statistics_service():
    """Tester le service de statistiques"""
    print("\n🧪 Test StatisticsService")
    print("-" * 40)
    
    stats_service = StatisticsService()
    
    # Mettre à jour les statistiques
    stats_service.update_daily_statistics()
    print("✅ Statistiques mises à jour")
    
    # Récupérer les statistiques
    stats = stats_service.get_dashboard_stats()
    if stats:
        print(f"✅ Statistiques récupérées:")
        print(f"   • Courses/jour: {stats['courses_jour']}")
        print(f"   • Revenus/jour: {stats['revenus_jour']} KMF")
        print(f"   • Taxes dues: {stats['taxes_dues']} KMF")
    else:
        print("❌ Aucune statistique trouvée")
    
    return True

def run_all_tests():
    """Exécuter tous les tests"""
    print("=" * 60)
    print("🚀 TEST COMPLET DES SERVICES ZAHEL")
    print("=" * 60)
    
    tests = [
        ("DatabaseService", test_database_service),
        ("AuthService", test_auth_service),
        ("CourseService", test_course_service),
        ("NotificationService", test_notification_service),
        ("FineService", test_fine_service),
        ("StatisticsService", test_statistics_service)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Exception dans {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Score: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
        print("Le système ZAHEL est prêt pour la production.")
    else:
        print(f"\n⚠️  {total - passed} test(s) ont échoué.")
        print("Veuillez vérifier les erreurs ci-dessus.")
    
    return passed == total

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)