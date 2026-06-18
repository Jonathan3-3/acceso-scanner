$DirectorioProyecto = "C:\Users\Jonathan Perez\acceso_scanner"

Set-Location -LiteralPath $DirectorioProyecto

$env:DJANGO_SETTINGS_MODULE = "configuracion.ajustes"

Write-Host "[*] Iniciando servidor waitress en 0.0.0.0:8000 ..." -ForegroundColor Cyan
python -m waitress --host=0.0.0.0 --port=8000 configuracion.wsgi:application
