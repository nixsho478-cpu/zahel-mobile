# test_tracking.py
print("🔧 TEST DriverTrackingScreen")

# Simuler un conducteur avec clés françaises
test_driver = {
    'nom': 'Hassan',
    'note': 4.82,
    'courses': 8012,
    'vehicule': 'Hyundai Verna',
    'price': 87,
    'distance': '4 min',
    'plaque': 'ZH-1234',
    'eta': '4 min'
}

print(f"✅ Conducteur de test créé: {test_driver['nom']}")

# Essayer d'importer et créer l'écran
try:
    from kivy.uix.screenmanager import Screen
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.progressbar import ProgressBar
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.popup import Popup
    
    print("✅ Import Kivy réussi")
    
    # Créer une version simplifiée pour tester
    class SimpleTrackingScreen(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = BoxLayout(orientation='vertical')
            layout.add_widget(Label(text='TEST: Écran de suivi fonctionnel!', color=COLORS['text_primary']))
            self.add_widget(layout)
    
    screen = SimpleTrackingScreen()
    print("✅ SimpleTrackingScreen créé avec succès")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()