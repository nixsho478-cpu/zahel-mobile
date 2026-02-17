import sqlite3

conn = sqlite3.connect('database/zahel_secure.db')
cursor = conn.cursor()

# Compter avant
cursor.execute("SELECT COUNT(*) FROM courses WHERE statut = 'en_attente'")
before = cursor.fetchone()[0]
print(f"📊 Courses en_attente avant: {before}")

# Marquer les anciennes courses comme terminées
cursor.execute("""
    UPDATE courses 
    SET statut = 'terminee', 
        conducteur_id = 1,
        updated_at = datetime('now')
    WHERE statut = 'en_attente' 
    AND created_at < datetime('now', '-10 minutes')
""")
updated = cursor.rowcount

# Compter après
cursor.execute("SELECT COUNT(*) FROM courses WHERE statut = 'en_attente'")
after = cursor.fetchone()[0]

conn.commit()
conn.close()

print(f"✅ {updated} courses marquées comme terminées")
print(f"📊 Courses en_attente après: {after}")