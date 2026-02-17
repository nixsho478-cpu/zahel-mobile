# analyse_amendes.py
import sqlite3

db_path = r"C:\Users\USER\Desktop\zahel\database\zahel_secure.db"

print("=" * 60)
print("ANALYSE DE LA TABLE 'amendes' EXISTANTE")
print("=" * 60)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. Nombre total d'amendes
cursor.execute("SELECT COUNT(*) as total FROM amendes")
total = cursor.fetchone()['total']
print(f"📊 TOTAL AMENDES : {total}")

if total > 0:
    # 2. Détails des amendes
    print(f"\n📋 DERNIÈRES AMENDES ({min(total, 5)} premières) :")
    cursor.execute("""
        SELECT id, utilisateur_type, utilisateur_id, montant, 
               raison, statut, date_amende, date_paiement
        FROM amendes 
        ORDER BY date_amende DESC 
        LIMIT 5
    """)
    
    amendes = cursor.fetchall()
    for amende in amendes:
        print(f"\n  • ID: {amende['id']}")
        print(f"    Type: {amende['utilisateur_type']}")
        print(f"    Utilisateur ID: {amende['utilisateur_id']}")
        print(f"    Montant: {amende['montant']} KMF")
        print(f"    Raison: {amende['raison']}")
        print(f"    Statut: {amende['statut']}")
        print(f"    Date: {amende['date_amende']}")
        if amende['date_paiement']:
            print(f"    Paiement: {amende['date_paiement']}")

# 3. Statistiques par type
print(f"\n📈 STATISTIQUES PAR TYPE :")
cursor.execute("""
    SELECT utilisateur_type, COUNT(*) as count, 
           SUM(montant) as total_montant,
           AVG(montant) as moyenne
    FROM amendes 
    GROUP BY utilisateur_type
""")
stats = cursor.fetchall()
for stat in stats:
    print(f"  • {stat['utilisateur_type']}: {stat['count']} amendes")
    print(f"    Total: {stat['total_montant']} KMF")
    print(f"    Moyenne: {stat['moyenne']:.0f} KMF")

# 4. Statistiques par statut
print(f"\n📈 STATISTIQUES PAR STATUT :")
cursor.execute("""
    SELECT statut, COUNT(*) as count, SUM(montant) as total
    FROM amendes 
    GROUP BY statut
""")
statuts = cursor.fetchall()
for statut in statuts:
    print(f"  • {statut['statut']}: {statut['count']} amendes")
    print(f"    Total: {statut['total']} KMF")

# 5. Vérifier les clients qui ont des amendes impayées
print(f"\n🔍 CLIENTS AVEC AMENDES IMPAYÉES :")
cursor.execute("""
    SELECT c.telephone, c.nom, 
           COUNT(a.id) as nb_amendes,
           SUM(a.montant) as total_du
    FROM clients c
    JOIN amendes a ON c.id = a.utilisateur_id 
    WHERE a.utilisateur_type = 'client' 
      AND a.statut = 'impayee'
    GROUP BY c.id
""")
clients_impayes = cursor.fetchall()

if clients_impayes:
    for client in clients_impayes:
        print(f"  • {client['telephone']} ({client['nom']})")
        print(f"    Amendes: {client['nb_amendes']}")
        print(f"    Dû: {client['total_du']} KMF")
else:
    print("  ✅ Aucun client avec amendes impayées")

conn.close()

print("\n" + "=" * 60)
print("ANALYSE TERMINÉE")
print("=" * 60)
input("\nAppuie sur ENTRÉE pour quitter...")