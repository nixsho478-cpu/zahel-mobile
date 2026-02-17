# create_icons.py - Créer les icônes ZAHEL automatiquement
from PIL import Image, ImageDraw
import os

def create_icons():
    """Créer les 3 icônes pour ZAHEL"""
    
    # Créer le dossier assets s'il n'existe pas
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"📁 Dossier créé: {assets_dir}")
    
    # 1. ICÔNE VOITURE BLEUE
    img_car = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img_car)
    
    # Corps voiture (bleu)
    draw.rectangle([6, 10, 26, 20], fill=(0, 100, 255, 255))
    # Toit (bleu foncé)
    draw.rectangle([10, 6, 22, 10], fill=(0, 80, 200, 255))
    # Roues (noir)
    draw.ellipse([8, 18, 12, 22], fill=(0, 0, 0, 255))
    draw.ellipse([20, 18, 24, 22], fill=(0, 0, 0, 255))
    # Pare-brise (blanc)
    draw.polygon([(10, 10), (22, 10), (18, 6), (14, 6)], fill=(255, 255, 255, 200))
    
    img_car.save(os.path.join(assets_dir, "car_blue.png"))
    print("✅ Icône voiture créée: car_blue.png")
    
    # 2. ICÔNE PERSONNE ROUGE
    img_person = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img_person)
    
    # Tête (rouge clair)
    draw.ellipse([12, 4, 20, 12], fill=(255, 100, 100, 255))
    # Corps (rouge)
    draw.rectangle([14, 12, 18, 22], fill=(255, 50, 50, 255))
    # Bras
    draw.line([10, 14, 14, 16], fill=(255, 50, 50, 255), width=2)
    draw.line([18, 16, 22, 14], fill=(255, 50, 50, 255), width=2)
    # Jambes
    draw.line([14, 22, 12, 26], fill=(255, 50, 50, 255), width=2)
    draw.line([18, 22, 20, 26], fill=(255, 50, 50, 255), width=2)
    
    img_person.save(os.path.join(assets_dir, "person_red.png"))
    print("✅ Icône client créée: person_red.png")
    
    # 3. ICÔNE DRAPEAU VERT (DESTINATION)
    img_flag = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img_flag)
    
    # Mât (marron)
    draw.rectangle([14, 6, 16, 26], fill=(139, 69, 19, 255))
    # Drapeau (vert)
    draw.polygon([(16, 10), (26, 14), (16, 18)], fill=(50, 200, 50, 255))
    # Base (gris)
    draw.rectangle([10, 26, 22, 28], fill=(100, 100, 100, 255))
    
    img_flag.save(os.path.join(assets_dir, "flag_green.png"))
    print("✅ Icône destination créée: flag_green.png")
    
    print("\n🎨 Toutes les icônes ont été créées dans le dossier 'assets/'")
    print("   - car_blue.png (32x32)")
    print("   - person_red.png (32x32)")
    print("   - flag_green.png (32x32)")

if __name__ == "__main__":
    print("=" * 50)
    print("🖼️  CRÉATION DES ICÔNES ZAHEL")
    print("=" * 50)
    create_icons()