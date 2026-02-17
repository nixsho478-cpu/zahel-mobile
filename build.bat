@echo off
echo ========================================
echo BUILD ZAHEL POUR ANDROID
echo ========================================

set BUILD_PATH=C:\Users\USER\AppData\Local\Programs\Python\Python313\Scripts\buildozer.exe
set PROJECT_DIR=C:\Users\USER\Desktop\zahel

cd /d "%PROJECT_DIR%"

echo.
echo 1. Vérification de l'environnement...
"%BUILD_PATH%" --version

echo.
echo 2. Liste des cibles disponibles...
"%BUILD_PATH%" targets

echo.
echo 3. Lancement du build...
"%BUILD_PATH%" android debug

echo.
echo ========================================
echo BUILD TERMINE
echo ========================================
pause