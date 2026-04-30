@echo off
echo ========================================
echo   Activation de l'environnement virtuel
echo ========================================
echo.
echo Méthodes disponibles :
echo 1. PowerShell (recommandé si la politique est configurée)
echo 2. CMD Batch (toujours fonctionnel)
echo.
echo Pour utiliser PowerShell, exécutez d'abord :
echo   powershell -ExecutionPolicy Bypass -File fix_powershell_policy.ps1
echo.
echo Pour utiliser CMD Batch :
echo   env_zahel\Scripts\activate.bat
echo.
echo Test de l'environnement...
echo.

REM Essayer d'activer avec batch
call env_zahel\Scripts\activate.bat

REM Vérifier si l'activation a réussi
if errorlevel 1 (
    echo ✗ Erreur lors de l'activation avec batch
    echo.
    echo Solutions :
    echo 1. Exécutez le script de correction PowerShell
    echo 2. Utilisez directement : env_zahel\Scripts\python.exe
) else (
    echo ✓ Environnement virtuel activé avec succès !
    echo.
    echo Pour vérifier : python --version
    echo Pour désactiver : deactivate
)

pause