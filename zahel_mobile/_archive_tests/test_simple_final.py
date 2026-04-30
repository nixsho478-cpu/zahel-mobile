#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test simple final - Validation des corrections de couleur
"""
import os
os.environ['KIVY_NO_ARGS'] = '1'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp

# Configuration fenêtre
Window.size = (360, 640)
Window.clearcolor = get_color_from_hex('#121212')  # Fond sombre

# Couleurs pour le test
COLORS = {
    'background': get_color_from_hex('#121212'),
    'text_primary': get_color_from_hex('#FFFFFF'),
    'text_secondary': get_color_from_hex('#B0B0B0'),
    'primary': get_color_from_hex('#1A73E8'),
    'input_bg': get_color_from_hex('#2C2C2C'),
    'input_text': get_color_from_hex('#FFFFFF'),
}

class ModernInput(TextInput):
    """Champ de saisie moderne - Dark Mode CORRIGÉ"""
    def __init__(self, hint='', **kwargs):
        super().__init__(**kwargs)
        self.hint_text = hint
        self.hint_text_color = get_color_from_hex('#AAAAAA')  # Gris clair
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(50)
        self.font_size = sp(16)
        self.padding = [dp(15), dp(15), dp(15), dp(15)]
        self.background_normal = ''
        self.background_active = ''
        self.background_disabled_normal = ''
        self.background_disabled_active = ''
        self.background_color = get_color_from_hex('#2C2C2C')  # Fond plus clair
        self.foreground_color = get_color_from_hex('#FFFFFF')  # Texte BLANC
        self.cursor_color = get_color_from_hex('#FFFFFF')
        self.cursor_width = 2
        self.selection_color = get_color_from_hex('#4A90E2')
        self.disabled_foreground_color = get_color_from_hex('#777777')
        self.bind(focus=self.on_focus)
    
    def on_focus(self, instance, value):
        self.foreground_color = get_color_from_hex('#FFFFFF')
        self.background_color = get_color_from_hex('#2C2C2C')
    
    def on_text(self, instance, value):
        self.foreground_color = get_color_from_hex('#FFFFFF')

class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Test 1: Labels avec et sans couleur
        layout.add_widget(Label(
            text='TEST FINAL - Validation des corrections',
            color=COLORS['text_primary'],
            font_size=sp(20),
            bold=True
        ))
        
        layout.add_widget(Label(
            text='Label AVEC couleur (devrait être visible)',
            color=COLORS['text_primary'],
            font_size=sp(16)
        ))
        
        # Test 2: ModernInput corrigé
        input1 = ModernInput(hint='Entrez votre texte ici')
        layout.add_widget(input1)
        
        # Test 3: Button avec couleur
        btn = Button(
            text='Bouton de test',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=COLORS['primary'],
            color=get_color_from_hex('#FFFFFF')
        )
        layout.add_widget(btn)
        
        # Test 4: Label SANS couleur (pour comparaison)
        layout.add_widget(Label(
            text='Label SANS couleur (devrait être invisible)',
            font_size=sp(16)
        ))
        
        # Informations
        info = Label(
            text='\nRÉSULTATS ATTENDUS:\n'
                 '1. Les Labels avec "color" doivent être visibles\n'
                 '2. Le champ ModernInput doit avoir du texte visible\n'
                 '3. Le Label sans couleur doit être invisible',
            color=COLORS['text_secondary'],
            halign='center'
        )
        layout.add_widget(info)
        
        return layout

if __name__ == '__main__':
    TestApp().run()