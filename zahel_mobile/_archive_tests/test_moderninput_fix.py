#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test pour vérifier la classe ModernInput et corriger les problèmes de couleur
"""
import os
os.environ['KIVY_NO_ARGS'] = '1'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
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
        
        # Test 1: Label avec couleur
        layout.add_widget(Label(
            text='Test ModernInput corrigé',
            color=COLORS['text_primary'],
            font_size=sp(20),
            bold=True
        ))
        
        # Test 2: ModernInput corrigé
        input1 = ModernInput(hint='Entrez votre texte ici')
        layout.add_widget(input1)
        
        # Test 3: TextInput standard pour comparaison
        input2 = TextInput(
            text='TextInput standard',
            size_hint_y=None,
            height=dp(40),
            background_color=COLORS['input_bg'],
            foreground_color=COLORS['input_text']
        )
        layout.add_widget(input2)
        
        # Test 4: ModernInput avec texte pré-rempli
        input3 = ModernInput(hint='Mot de passe')
        input3.text = 'monmotdepasse'
        input3.password = True
        layout.add_widget(input3)
        
        # Informations
        info = Label(
            text='\nLe texte devrait être visible dans tous les champs.\nSi invisible, vérifier foreground_color et background_color.',
            color=COLORS['text_secondary'],
            halign='center'
        )
        layout.add_widget(info)
        
        return layout

if __name__ == '__main__':
    TestApp().run()