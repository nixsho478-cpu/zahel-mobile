# Script pour corriger les problèmes de politique d'exécution PowerShell
# qui causent l'erreur PSSecurityException lors de l'activation de l'environnement virtuel

Write-Host "=== Correction des problèmes de politique PowerShell ===" -ForegroundColor Cyan

# Afficher la politique actuelle
Write-Host "`n1. Politique d'exécution actuelle :" -ForegroundColor Yellow
Get-ExecutionPolicy -List

# Définir la politique RemoteSigned pour l'utilisateur courant
Write-Host "`n2. Définition de la politique RemoteSigned pour l'utilisateur courant..." -ForegroundColor Yellow
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Vérifier que la modification a été appliquée
Write-Host "`n3. Vérification de la nouvelle politique :" -ForegroundColor Yellow
$newPolicy = Get-ExecutionPolicy
Write-Host "   Politique d'exécution actuelle : $newPolicy" -ForegroundColor Green

# Tester l'activation de l'environnement virtuel
Write-Host "`n4. Test d'activation de l'environnement virtuel env_zahel..." -ForegroundColor Yellow
try {
    .\env_zahel\Scripts\Activate.ps1
    Write-Host "   ✓ Activation réussie !" -ForegroundColor Green
    Write-Host "   Environnement virtuel activé : $env:VIRTUAL_ENV" -ForegroundColor Green
    
    # Tester Python
    Write-Host "`n5. Test de Python dans l'environnement virtuel..." -ForegroundColor Yellow
    python --version
    Write-Host "   ✓ Python fonctionne correctement" -ForegroundColor Green
    
    # Désactiver l'environnement
    deactivate
    Write-Host "`n6. Environnement désactivé avec succès." -ForegroundColor Green
    
} catch {
    Write-Host "   ✗ Erreur lors de l'activation : $_" -ForegroundColor Red
    Write-Host "`nSolution alternative :" -ForegroundColor Yellow
    Write-Host "   Utilisez le script batch à la place :" -ForegroundColor White
    Write-Host "   .\env_zahel\Scripts\activate.bat" -ForegroundColor White
}

Write-Host "`n=== Correction terminée ===" -ForegroundColor Cyan
Write-Host "`nInstructions pour utiliser l'environnement virtuel :" -ForegroundColor Yellow
Write-Host "1. Pour PowerShell : .\env_zahel\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Pour CMD : .\env_zahel\Scripts\activate.bat" -ForegroundColor White
Write-Host "3. Pour désactiver : deactivate" -ForegroundColor White