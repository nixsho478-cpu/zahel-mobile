# test_prices.py
def round_to_comoros(amount):
    """Arrondir au multiple de 25 KMF supérieur"""
    multiple = 25
    return ((amount + multiple - 1) // multiple) * multiple

def calculate_price(distance_km, service_type):
    """Calculer prix selon service"""
    tarifs_km = {
        'standard': 300,
        'comfort': 400, 
        'moto': 200,
    }
    
    tarif = tarifs_km.get(service_type, 300)
    prix_base = distance_km * tarif
    prix_arrondi = round_to_comoros(prix_base)
    
    prix_minimum = {
        'standard': 500,
        'comfort': 750,
        'moto': 300,
    }
    
    return max(prix_arrondi, prix_minimum.get(service_type, 500))

# Tests
test_cases = [
    (1.0, 'standard'),  # 1km standard
    (2.5, 'standard'),  # 2.5km standard  
    (0.8, 'moto'),      # 0.8km moto
    (3.0, 'comfort'),   # 3km comfort
    (10.0, 'standard'), # 10km standard
]

print("🧪 TESTS DE CALCUL DE PRIX")
print("=" * 40)
for distance, service in test_cases:
    prix = calculate_price(distance, service)
    print(f"{distance}km - {service}: {prix} KMF")