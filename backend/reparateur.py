import sqlite3
import time

def reparer_apres_course():
    conn = sqlite3.connect('../database/zahel_secure.db')
    cursor = conn.cursor()
    
    # Pour tous les conducteurs avec courses terminées mais indisponibles
    cursor.execute("""
        UPDATE conducteurs 
        SET disponible = 1, 
            en_course = 0
        WHERE id IN (
            SELECT DISTINCT c.id
            FROM conducteurs c
            LEFT JOIN courses co ON co.conducteur_id = c.id 
                AND co.statut IN ('en_cours', 'acceptee')
            WHERE c.disponible = 0 
               OR c.en_course = 1
            GROUP BY c.id
            HAVING COUNT(co.id) = 0  -- Aucune course en cours
        )
    """)
    
    rows = cursor.rowcount
    if rows > 0:
        print(f"✅ {rows} conducteur(s) réparé(s)")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("🛠️  Réparateur automatique démarré...")
    while True:
        reparer_apres_course()
        time.sleep(5)  # Vérifie toutes les 5 secondes
