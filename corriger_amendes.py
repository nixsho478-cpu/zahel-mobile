# corriger_amendes.py
import sqlite3
import json

print('🔄 CORRECTION DES AMENDES ET STATISTIQUES')
print('='*60)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# 1. Voir toutes les amendes
cursor.execute('SELECT id, utilisateur_type, utilisateur_id, montant, statut, raison FROM amendes')
amendes = cursor.fetchall()

print(f'📋 {len(amendes)} amende(s) trouvée(s) :')
print('-' * 60)

total_amendes_dues = 0
total_amendes_payees = 0

for amende in amendes:
    amende_id, user_type, user_id, montant, statut, raison = amende
    
    # Trouver le nom de l'utilisateur
    if user_type == 'client':
        cursor.execute('SELECT telephone, nom FROM clients WHERE id = ?', (user_id,))
    else:
        cursor.execute('SELECT immatricule, nom FROM conducteurs WHERE id = ?', (user_id,))
    
    user_info = cursor.fetchone()
    nom_utilisateur = user_info[1] if user_info else f'ID:{user_id}'
    contact = user_info[0] if user_info else 'N/A'
    
    print(f'#{amende_id} | {user_type.upper():10} | {nom_utilisateur:20} | {montant:8} KMF | {statut:12} | {raison[:40]}...')
    
    if statut == 'en_attente':
        total_amendes_dues += montant
    elif statut == 'payee':
        total_amendes_payees += montant

print('-' * 60)
print(f'\n💰 TOTAL :')
print(f'  • Amendes en attente : {total_amendes_dues} KMF')
print(f'  • Amendes payées     : {total_amendes_payees} KMF')
print(f'  • Total général      : {total_amendes_dues + total_amendes_payees} KMF')

# 2. Vérifier les statistiques actuelles
print('\n📊 STATISTIQUES AVANT CORRECTION :')
cursor.execute('SELECT amendes_dues, amendes_payees FROM statistiques WHERE id = 1')
stats = cursor.fetchone()

if stats:
    print(f'  • Amendes dues (DB)   : {stats[0]} KMF')
    print(f'  • Amendes payées (DB) : {stats[1]} KMF')
    
    # Calculer la différence
    diff_dues = total_amendes_dues - stats[0]
    diff_payees = total_amendes_payees - stats[1]
    
    print(f'\n⚠️ DIFFÉRENCES :')
    print(f'  • Amendes dues   : {diff_dues} KMF ({stats[0]} → {total_amendes_dues})')
    print(f'  • Amendes payées : {diff_payees} KMF ({stats[1]} → {total_amendes_payees})')

# 3. Corriger les statistiques
print('\n🔧 CORRECTION DES STATISTIQUES...')

cursor.execute('''
    UPDATE statistiques 
    SET amendes_dues = ?,
        amendes_payees = ?
    WHERE id = 1
''', (total_amendes_dues, total_amendes_payees))

conn.commit()

# 4. Vérifier après correction
cursor.execute('SELECT amendes_dues, amendes_payees FROM statistiques WHERE id = 1')
stats_corrigees = cursor.fetchone()

print(f'\n✅ STATISTIQUES APRÈS CORRECTION :')
print(f'  • Amendes dues   : {stats_corrigees[0]} KMF')
print(f'  • Amendes payées : {stats_corrigees[1]} KMF')

# 5. Mettre à jour aussi les finances si besoin
print('\n💡 CONSEIL :')
print('  1. Redémarrez le serveur : cd backend && python api_zahel.py')
print('  2. Rafraîchissez le dashboard')
print('  3. Vérifiez que les amendes s\'affichent correctement')

conn.close()
print('\n🎯 CORRECTION TERMINÉE !')