# mapbox_state.py
class MapboxState:
    markers = []
    route = []
    depart = None
    arrivee = None
    confirmed = False
    
    @classmethod
    def add_marker(cls, lat, lng, marker_type):
        cls.markers.append({'lat': lat, 'lng': lng, 'type': marker_type})
        print(f"📍 Marqueur ajouté: {marker_type} à ({lat}, {lng})")
    
    @classmethod
    def set_depart(cls, lat, lng):
        cls.depart = {'lat': lat, 'lng': lng}
        print(f"📍 Départ défini: ({lat}, {lng})")
    
    @classmethod
    def set_arrivee(cls, lat, lng):
        cls.arrivee = {'lat': lat, 'lng': lng}
        print(f"🏁 Arrivée définie: ({lat}, {lng})")
    
    @classmethod
    def set_route(cls, coordinates):
        cls.route = coordinates
        print(f"🛣️ Route définie: {len(coordinates)} points")
    
    @classmethod
    def set_confirmed(cls, confirmed):
        cls.confirmed = confirmed
        print(f"✅ Confirmation: {confirmed}")
    
    @classmethod
    def clear(cls):
        cls.markers = []
        cls.route = []
        cls.depart = None
        cls.arrivee = None
        cls.confirmed = False
        print("🧹 État effacé")
    
    @classmethod
    def get_state(cls):
        return {
            'markers': cls.markers,
            'route': cls.route,
            'depart': cls.depart,
            'arrivee': cls.arrivee,
            'confirmed': cls.confirmed
        }