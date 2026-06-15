@echo off
echo ========================================
echo  Instalar sincronizacion automatica FCX
echo ========================================
echo.

set "BATCH=C:\Users\Jonathan Perez\acceso_scanner\scripts\sync_device.bat"

:: Eliminar tarea anterior si existe
schtasks /delete /tn "SyncFCX" /f >nul 2>&1

:: Crear tarea apuntando al .bat (que ya tiene ruta completa y cd)
schtasks /create /tn "SyncFCX" /tr "'%BATCH%'" /sc minute /mo 1 /ru SYSTEM /rl HIGHEST /f

echo.
echo [OK] Tarea instalada. Se ejecuta cada 1 minuto.
echo Ruta: %BATCH%
echo.
echo Para probar manual:
echo   cd /d "C:\Users\Jonathan Perez\acceso_scanner"
echo   python manage.py sync_device
pause
