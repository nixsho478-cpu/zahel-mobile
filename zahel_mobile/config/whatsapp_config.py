# ============================================
# CONFIGURATION WHATSAPP ZAHEL
# ============================================

WHATSAPP_CONFIG = {
    # NUMÉRO DE L'AGENCE (format international sans +)
    'AGENCE_NUMBER': '+2693608657',  # ← REMPLACE PAR TON NUMÉRO
    
    # MESSAGE PRÉ-REMPLI POUR CONDUCTEURS
    'MESSAGE_TEMPLATE': {
        'confort': """Immatricule: {immatricule}
Catégorie: CONFORT

📋 DOCUMENTS :
1. CNI/Passeport
2. Permis de conduire
3. Carte grise

🚗 PHOTOS EXTÉRIEUR :
4. Face avant
5. Face arrière
6. Côté conducteur
7. Côté passager

🛋️ PHOTOS INTÉRIEUR :
8. Sièges avant
9. Tableau de bord

Merci de vérification ZAHEL ✅""",

        'luxe': """Immatricule: {immatricule}
Catégorie: LUXE

📋 DOCUMENTS :
1. CNI/Passeport
2. Permis de conduire
3. Carte grise

🚗 PHOTOS EXTÉRIEUR :
4. Face avant
5. Face arrière
6. Côté conducteur
7. Côté passager

🛋️ PHOTOS INTÉRIEUR :
8. Sièges avant
9. Tableau de bord
10. Sièges arrière
11. Toit ouvrant (si équipé)

Merci de vérification ZAHEL ✅"""
    },
    
    # MESSAGE POUR STANDARD/MOTO (pas de vérification)
    'MESSAGE_SUCCESS': """Félicitations {nom} !

Votre inscription ZAHEL est immédiatement active.
Immatricule: {immatricule}

Vous pouvez vous connecter et recevoir des courses dès maintenant.

Bienvenue dans la famille ZAHEL ! 🚗💨"""
}