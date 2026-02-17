# test_minimal.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class TestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Écran de test'))
        btn = Button(text='Test OK')
        layout.add_widget(btn)
        self.add_widget(layout)

class TestApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TestScreen(name='test'))
        return sm

if __name__ == '__main__':
    TestApp().run()