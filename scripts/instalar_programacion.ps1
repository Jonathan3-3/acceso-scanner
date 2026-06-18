$NombreTarea = "SyncFCX"
$DirectorioProyecto = "C:\Users\Jonathan Perez\acceso_scanner"

$Accion = New-ScheduledTaskAction -Execute "python" -Argument "manage.py sincronizar_dispositivo" -WorkingDirectory $DirectorioProyecto
$Disparador = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration ([TimeSpan]::MaxValue)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$Configuracion = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::MaxValue)

Unregister-ScheduledTask -TaskName $NombreTarea -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $NombreTarea -Action $Accion -Trigger $Disparador -Principal $Principal -Settings $Configuracion -Force

Write-Host "[OK] Tarea '$NombreTarea' instalada. Sincroniza cada 1 minuto." -ForegroundColor Green
