# force_update_stats.py
import sqlite3

print('🔄 FORCE UPDATE STATISTIQUES')
print('='*50)

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Forcer la valeur à 500 KMF (votre amende)
cursor.execute('UPDATE statistiques SET amendes_dues = 500 WHERE id = 1')
conn.commit()

# Vérifier
cursor.execute('SELECT amendes_dues, amendes_payees FROM statistiques WHERE id = 1')
stats = cursor.fetchone()
print(f'✅ Stats mises à jour : {stats[0]} KMF dues, {stats[1]} KMF payées')

conn.close()
print('🎯 Dashboard devrait maintenant afficher 500 KMF')