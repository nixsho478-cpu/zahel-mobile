# test_map_selection.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from map_selection_screen import MapSelectionScreen


class TestApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Créer un client API simulé
        class MockAPIClient:
            def geocode_address(self, address):
                return {'success': True, 'latitude': -11.698, 'longitude': 43.256, 'place_name': address}
        
        # Créer l'écran
        screen = MapSelectionScreen(name='map')
        
        # Ajouter l'API client
        screen.api_client = MockAPIClient()
        
        sm.add_widget(screen)
        sm.current = 'map'
        return sm


if __name__ == '__main__':
    TestApp().run()