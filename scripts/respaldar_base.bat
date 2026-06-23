@echo off
title Respaldo Base de Datos - Acceso Scanner
setlocal enabledelayedexpansion

echo ============================================
echo  RESPALDO DE BASE DE DATOS
echo  Acceso Scanner
echo ============================================
echo.

:: Leer credenciales desde .env
set ENV_FILE=C:\Users\Usuario\Desktop\acceso_scanner\.env
if not exist "%ENV_FILE%" (
    echo [ERROR] No se encuentra el archivo .env
    echo Ruta esperada: %ENV_FILE%
    pause
    exit /b 1
)

for /f "tokens=1,* delims==" %%a in ('type "%ENV_FILE%"') do (
    set "linea=%%a"
    if /i "!linea!"=="DB_NAME" set DB_NAME=%%b
    if /i "!linea!"=="DB_USER" set DB_USER=%%b
    if /i "!linea!"=="DB_PASSWORD" set DB_PASSWORD=%%b
    if /i "!linea!"=="DB_HOST" set DB_HOST=%%b
    if /i "!linea!"=="DB_PORT" set DB_PORT=%%b
)

if "%DB_NAME%"=="" (
    echo [ERROR] No se pudo leer DB_NAME del .env
    pause
    exit /b 1
)

set FECHA=%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set FECHA=%FECHA: =0%
set ARCHIVO=C:\Users\Usuario\Desktop\respaldos\respaldo_%FECHA%.sql

if not exist "C:\Users\Usuario\Desktop\respaldos" mkdir "C:\Users\Usuario\Desktop\respaldos"

echo Base de datos: %DB_NAME%
echo Archivo: %ARCHIVO%
echo.

"C:\xampp\mysql\bin\mysqldump" -h %DB_HOST% -u %DB_USER% -p%DB_PASSWORD% %DB_NAME% > "%ARCHIVO%"

if %ERRORLEVEL% EQU 0 (
    echo [OK] Respaldo creado exitosamente
    echo Archivo: %ARCHIVO%
) else (
    echo [ERROR] Fallo al crear el respaldo
)

echo.
pause
