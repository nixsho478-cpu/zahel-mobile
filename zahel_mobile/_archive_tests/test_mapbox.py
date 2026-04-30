# test_mapbox.py - Test simple de la carte Mapbox
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from mapbox_mapview import MapboxMapView


class TestMapboxApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        # Créer la carte
        self.map = MapboxMapView(
            lat=-11.6980,  # Moroni
            lng=43.2560,
            zoom=14,
            size_hint=(1, 0.9)
        )
        
        # Boutons de contrôle
        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        btn_zoom_in = Button(text='+ Zoom')
        btn_zoom_in.bind(on_press=lambda x: self.map.zoom_in())
        
        btn_zoom_out = Button(text='- Zoom')
        btn_zoom_out.bind(on_press=lambda x: self.map.zoom_out())
        
        btn_center = Button(text='↺ Centre')
        btn_center.bind(on_press=lambda x: self.map.center_on(-11.6980, 43.2560))
        
        btn_layout.add_widget(btn_zoom_in)
        btn_layout.add_widget(btn_zoom_out)
        btn_layout.add_widget(btn_center)
        
        layout.add_widget(self.map)
        layout.add_widget(btn_layout)
        
        return layout


if __name__ == '__main__':
    TestMapboxApp().run()