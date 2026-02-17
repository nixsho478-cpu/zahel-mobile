# verifier_tables.py
import sqlite3

print("🔍 VÉRIFICATION DES TABLES ZAHEL")
print("="*50)

try:
    conn = sqlite3.connect('zahel_secure.db')
    cursor = conn.cursor()
    
    # 1. Toutes les tables
    print("\n📋 TOUTES LES TABLES:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    for table in tables:
        print(f"  - {table[0]}")
    
    # 2. Vérifier spécifiquement 'statistiques'
    print("\n📊 TABLE 'STATISTIQUES':")
    if 'statistiques' in [t[0] for t in tables]:
        print("  ✅ Table existe")
        
        # Voir les colonnes
        cursor.execute("PRAGMA table_info(statistiques)")
        cols = cursor.fetchall()
        
        print(f"  {len(cols)} colonnes:")
        for col in cols:
            print(f"    {col[0]}. {col[1]:20} {col[2]}")
            
        # Vérifier les colonnes importantes
        colonnes_trouvees = [col[1] for col in cols]
        if 'amendes_dues' in colonnes_trouvees:
            print("  ✅ amendes_dues: PRÉSENTE")
        else:
            print("  ❌ amendes_dues: ABSENTE")
            
        if 'amendes_payees' in colonnes_trouvees:
            print("  ✅ amendes_payees: PRÉSENTE")
        else:
            print("  ❌ amendes_payees: ABSENTE")
            
    else:
        print("  ❌ Table 'statistiques' n'existe pas!")
        
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")

print("\n" + "="*50)
print("✅ Vérification terminée")