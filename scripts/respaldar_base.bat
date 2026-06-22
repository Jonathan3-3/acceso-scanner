@echo off
title Respaldo Base de Datos - Acceso Scanner
echo ============================================
echo  RESPALDO DE BASE DE DATOS
echo  Acceso Scanner - luisen47_LGA
echo ============================================
echo.

set FECHA=%DATE:~0,2%%DATE:~3,2%%DATE:~6,4%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set FECHA=%FECHA: =0%
set ARCHIVO=C:\Users\Usuario\Desktop\respaldos\respaldo_%FECHA%.sql

if not exist "C:\Users\Usuario\Desktop\respaldos" mkdir "C:\Users\Usuario\Desktop\respaldos"

echo Respaldando en: %ARCHIVO%
echo.

"C:\xampp\mysql\bin\mysqldump" -h 127.0.0.1 -u luisen47_garrom -pGarrom.2023 luisen47_LGA > "%ARCHIVO%"

if %ERRORLEVEL% EQU 0 (
    echo [OK] Respaldo creado exitosamente
    echo Archivo: %ARCHIVO%
) else (
    echo [ERROR] Fallo al crear el respaldo
)

echo.
pause
