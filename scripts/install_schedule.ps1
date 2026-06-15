$TaskName = "SyncFCX"
$PythonExe = "C:\Users\Jonathan Perez\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$ProjectDir = "C:\Users\Jonathan Perez\acceso_scanner"

$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "manage.py sync_device" -WorkingDirectory $ProjectDir
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration ([TimeSpan]::MaxValue)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::MaxValue)

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

Write-Host "[OK] Tarea '$TaskName' instalada. Sincroniza cada 1 minuto." -ForegroundColor Green
