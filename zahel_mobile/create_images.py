# create_images.py
from PIL import Image, ImageDraw
import os

# Créer le dossier si nécessaire
os.makedirs("images", exist_ok=True)

# 1. driver_icon.png - Voiture bleue
img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)
# Carré bleu
draw.rectangle([4, 4, 28, 28], fill=(0, 100, 255, 255))
# Lettre D blanche
draw.text((10, 8), "D", fill=(255, 255, 255, 255))
img.save("images/driver_icon.png")

# 2. client_icon.png - Personne verte  
img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)
# Cercle vert
draw.ellipse([4, 4, 28, 28], fill=(0, 200, 100, 255))
# Lettre C blanche
draw.text((10, 8), "C", fill=(255, 255, 255, 255))
img.save("images/client_icon.png")

# 3. flag_green.png - Drapeau vert
img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)
# Triangle vert
draw.polygon([(16, 4), (28, 28), (4, 28)], fill=(0, 200, 100, 255))
img.save("images/flag_green.png")

print("✅ Images créées dans le dossier images/")