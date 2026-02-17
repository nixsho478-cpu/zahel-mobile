import os
import sys
import subprocess

print("🚀 BUILD SIMPLIFIÉ POUR ZAHEL")
print("=" * 50)

# Chemin de Buildozer
buildozer_exe = r"C:\Users\USER\AppData\Local\Programs\Python\Python313\Scripts\buildozer.exe"

# Commande
cmd = [buildozer_exe, "android", "debug"]
print(f"Commande: {' '.join(cmd)}")

# Exécute
try:
    result = subprocess.run(cmd, 
                          capture_output=True, 
                          text=True,
                          shell=True)
    
    print("Sortie standard:")
    print(result.stdout)
    
    if result.stderr:
        print("\nErreurs:")
        print(result.stderr)
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "=" * 50)
input("Appuyez sur Entrée pour quitter...")