import os
import sys
import subprocess

print("🚀 BUILD SIMPLIFIÉ POUR ZAHEL")
print("=" * 50)

# ⭐ CORRECTION : Chemin vers buildozer.exe dans l'environnement virtuel
buildozer_exe = r"C:\Users\USER\Desktop\zahel\env_zahel\Scripts\buildozer.exe"

# Vérifier que le fichier existe
if not os.path.exists(buildozer_exe):
    print(f"❌ Buildozer non trouvé: {buildozer_exe}")
    print("Vérifiez que vous êtes dans l'environnement virtuel")
    input("Appuyez sur Entrée pour quitter...")
    sys.exit(1)

# Commande
cmd = [buildozer_exe, "android", "debug"]
print(f"Commande: {' '.join(cmd)}")

# Exécute
try:
    result = subprocess.run(cmd, 
                          capture_output=True, 
                          text=True,
                          cwd=r"C:\Users\USER\Desktop\zahel")
    
    print("\n" + "=" * 50)
    print("SORTIE STANDARD:")
    print("=" * 50)
    print(result.stdout)
    
    if result.stderr:
        print("\n" + "=" * 50)
        print("ERREURS:")
        print("=" * 50)
        print(result.stderr)
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "=" * 50)
input("Appuyez sur Entrée pour quitter...")