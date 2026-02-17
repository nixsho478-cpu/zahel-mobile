# test_kivy_simple.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window

Window.size = (360, 640)

class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Test API
        import requests
        try:
            r = requests.get('http://localhost:5001/api/courses/disponibles', 
                           headers={'Authorization': 'ZH-327KYM'})
            data = r.json()
            
            if data.get('success'):
                count = data.get('count', 0)
                layout.add_widget(Label(
                    text=f'✅ API OK: {count} courses',
                    font_size=20,
                    color=(0, 1, 0, 1)
                ))
                
                if count > 0:
                    for course in data.get('courses', [])[:3]:  # 3 premières
                        layout.add_widget(Label(
                            text=f"{course.get('code')} - {course.get('prix_convenu')} KMF",
                            font_size=16
                        ))
            else:
                layout.add_widget(Label(
                    text=f'❌ API Error: {data.get("error")}',
                    font_size=20,
                    color=(1, 0, 0, 1)
                ))
                
        except Exception as e:
            layout.add_widget(Label(
                text=f'💥 Exception: {e}',
                font_size=20,
                color=(1, 0, 0, 1)
            ))
        
        return layout

if __name__ == '__main__':
    TestApp().run()