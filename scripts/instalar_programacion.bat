@echo off
echo ========================================
echo  Instalar sincronizacion automatica FCX
echo ========================================
echo.

set "BAT=C:\Users\Jonathan Perez\acceso_scanner\scripts\sincronizar_dispositivo.bat"

schtasks /delete /tn "SyncFCX" /f >nul 2>&1
schtasks /create /tn "SyncFCX" /tr "'%BAT%'" /sc minute /mo 1 /ru SYSTEM /rl HIGHEST /f

echo.
echo [OK] Tarea instalada. Se ejecuta cada 1 minuto.
echo Ruta: %BAT%
echo.
echo Para probar manual:
echo   cd /d "C:\Users\Jonathan Perez\acceso_scanner"
echo   python manage.py sincronizar_dispositivo
pause
