Write-Host "Test PowerShell Script"
$policy = Get-ExecutionPolicy
Write-Host "Current Execution Policy: $policy"
Write-Host "Trying to activate virtual environment..."
try {
    .\env_zahel\Scripts\Activate.ps1
    Write-Host "Activation successful!"
} catch {
    Write-Host "Error: $_"
}