@echo off
echo ========================================
echo     DEMARRAGE COMPLET ZAHEL
echo ========================================

echo [1/4] Demarrage Backend API...
start "ZAHEL Backend" cmd /k "cd backend && python api_zahel.py"

timeout /t 2 /nobreak >nul

echo [2/4] Demarrage Proxy Nominatim...
start "ZAHEL Proxy" cmd /k "cd zahel_mobile && python nominatim_proxy.py"

timeout /t 2 /nobreak >nul

echo [3/4] Demarrage Client...
start "ZAHEL Client" cmd /k "cd zahel_mobile && python main.py"

echo [4/4] Demarrage Conducteur...
start "ZAHEL Conducteur" cmd /k "cd zahel_mobile && python main.py --driver"

echo.
echo ========================================
echo ✅ ZAHEL EST PRET !
echo ========================================
echo.
echo Backend:    http://localhost:5001
echo Proxy:      http://localhost:5002
echo Client:     Application Kivy
echo Conducteur: Application Kivy
echo.
pause