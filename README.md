# Control de Acceso — FCX (ZKTeco)

Sistema web Django para gestionar registros de asistencia del dispositivo
**FCX** (ZMM220_TFT). Sincroniza automáticamente vía PULL (pyzk/TCP 4370),
muestra entrada/salida por empleado por día y ofrece dashboard en tiempo real.

---

## Estructura del proyecto

```
acceso_scanner/
├── apps/
│   ├── attendance/           # App de asistencia
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── sync_device.py   # Comando: python manage.py sync_device
│   │   ├── migrations/               # Migraciones de la BD
│   │   ├── models.py                 # ScanRecord (huella individual)
│   │   ├── pull.py                   # Sincronización PULL con pyzk
│   │   ├── push.py                   # Stubs PUSH (ZKTeco HTTP)
│   │   ├── services.py               # Lógica: reportes, matching, .DAT
│   │   ├── urls.py                   # Rutas de la app
│   │   └── views.py                  # Dashboard, APIs, detalle empleado
│   ├── employees/             # App de empleados
│   │   ├── management/
│   │   ├── migrations/
│   │   │   └── 0002_load_employees.py  # 27 empleados iniciales
│   │   └── models.py                 # Employee (raw_id, name)
│   └── __init__.py
├── config/                    # Configuración Django
│   ├── settings.py            # MySQL, Timezone, STATICFILES_DIRS
│   ├── urls.py                # Rutas raíz
│   └── wsgi.py                # WSGI para producción
├── frontend/                  # Frontend (separado de Django)
│   ├── static/
│   │   ├── css/style.css      # Estilos personalizados (drop-zone, pulse, fade-in)
│   │   └── js/main.js         # Lógica del dashboard (polling, upload, animaciones)
│   └── templates/
│       ├── attendance/
│       │   ├── dashboard.html           # Dashboard principal
│       │   └── employee_detail.html     # Detalle por empleado
│       └── base.html                    # Layout base (Bootstrap 5 dark)
├── scripts/                   # Scripts de despliegue
│   ├── install_schedule.bat   # Instalar tarea programada (cada 1 min)
│   ├── install_schedule.ps1   # Versión PowerShell con WorkingDirectory
│   └── sync_device.bat        # Script que corre la sincronización
├── manage.py                  # Punto de entrada Django
└── requirements.txt           # Dependencias
```

---

## Requisitos

- **Python** ≥ 3.10
- **MySQL** 8.0+ (base de datos `acceso_scanner`)
- **Dispositivo FCX** (ZMM220_TFT) en red local

## Instalación

### 1. Clonar e instalar dependencias

```bash
cd acceso_scanner
pip install -r requirements.txt
```

### 2. Crear base de datos MySQL

```sql
CREATE DATABASE acceso_scanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Las credenciales en `config/settings.py`:

| Campo     | Valor       |
|-----------|-------------|
| Usuario   | root        |
| Password  | G@RR0M     |
| Host      | 127.0.0.1  |
| Puerto    | 3306       |

### 3. Migrar base de datos

```bash
python manage.py migrate
```

Esto crea las tablas y carga los **27 empleados** iniciales (data migration).

### 4. Verificar

```bash
python manage.py check
```

---

## Uso

### Iniciar servidor

```bash
python manage.py runserver
```

Abrir **http://localhost:8000/** en el navegador.

### Sincronización manual con el FCX

```bash
python manage.py sync_device
```

Conecta al dispositivo `10.10.0.3:4370`, descarga:
- **Empleados nuevos** (los crea en MySQL automáticamente)
- **Registros de asistencia nuevos** (los vincula al empleado correspondiente)

### Sincronización automática (cada 1 minuto)

Abrir PowerShell como **Administrador** y ejecutar:

```powershell
& "C:\Users\Jonathan Perez\acceso_scanner\scripts\install_schedule.bat"
```

Esto instala la tarea programada `SyncFCX` que corre cada minuto en segundo plano.

Para verificar:
```cmd
schtasks /query /tn SyncFCX
```

### Subir archivo .DAT manual

En el dashboard, arrastra un archivo .DAT (formato tab-separado: `AER0000142\t2024-08-26 07:16:30`) o haz clic para seleccionarlo. El sistema procesa, empareja empleados y muestra el reporte.

---

## API endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Dashboard HTML |
| GET | `/employee/<pk>/` | Detalle HTML de un empleado |
| GET | `/api/report/?date=YYYY-MM-DD` | Reporte diario (JSON) |
| GET | `/api/recent-scans/` | Últimos 20 registros (JSON) |
| GET | `/api/sync-status/` | Estado del dispositivo (JSON) |
| GET | `/api/employees/` | Lista de empleados (JSON) |
| GET | `/api/employee/<pk>/detail/?from=YYYY-MM-DD&to=YYYY-MM-DD` | Detalle de empleado por rango (JSON) |
| POST | `/upload/` | Subir archivo .DAT (multipart) |

### Ejemplo: detalle por empleado

```
GET /api/employee/5/detail/?from=2026-06-01&to=2026-06-10
```

```json
{
  "employee": { "id": 5, "display_id": "AER149", "name": "FELIPE DE JESUS TAPIA GARCIA" },
  "date_from": "2026-06-01",
  "date_to": "2026-06-10",
  "days": [
    { "date": "2026-06-10", "first_scan": "07:02:00", "last_scan": "17:30:00", "hours": 10.47 }
  ],
  "summary": { "total_days": 1, "total_hours": 10.47, "avg_hours": 10.47 }
}
```

---

## Dashboard en vivo

- **Polling**: cada 5 segundos consulta `/api/recent-scans/` y muestra nuevos registros con badge **NUEVO**
- **Sincronización**: cada 1 minuto el `sync_device` trae datos del FCX
- **Estadísticas**: empleados, registros hoy, total registros, estado del dispositivo

### Filtros en detalle de empleado

Cada nombre de empleado es clickable. La página de detalle ofrece:

| Botón | Rango |
|-------|-------|
| Hoy | Hoy |
| Ayer | Día anterior |
| Esta semana | Lunes a domingo actual |
| Semana pasada | Lunes a domingo anterior |
| Este mes | 1° del mes a hoy |
| Mes pasado | 1° al último día del mes anterior |
| Personalizado | Cualquier rango con input type="date" |

---

## Flujo de datos

```
AccessPRO (app escritorio)
    ↓  (sincronización manual al dispositivo)
FCX (ZMM220_TFT)
    │  IP: 10.10.0.3  ·  Puerto: 4370  ·  Serial: AEYU194660027
    │
    ├── PULL → pyzk → SyncDevice (cada 1 min)
    │        ↓
    │   ScanRecord (MySQL)
    │        ↓
    │   Dashboard / API
    │
    └── PUSH → /iclock/cdata   (stub, sin implementar)
```

### Modelo de datos

```
Employee              ScanRecord
─────────             ─────────────────
raw_id (PK)           id (PK)
name                  employee → Employee (FK)
                      scanned_at (datetime)
                      raw_data (text)
                      device_sn (varchar)
                      created_at (datetime, auto)
```

- Cada `ScanRecord` es **una huella individual** del dispositivo
- El cálculo entrada/salida agrupa por `employee + date`, toma `min(scanned_at)` y `max(scanned_at)`
- Los `display_id` se formatean como `AER###` (ej. `AER142`)
- Los `raw_id` guardan el formato original (`AER0000142`)

---

## Solución de problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| `sync_device` falla | Dispositivo no alcanzable | Verificar IP/firewall: `ping 10.10.0.3` |
| La tarea SyncFCX no corre | Falta directorio de trabajo | Usar `install_schedule.ps1` con `-WorkingDirectory` |
| Dashboard muestra "Sin registros" | No se ha sincronizado | `python manage.py sync_device` |
| Empleado no aparece en reporte | No está en MySQL | Agregarlo en AccessPRO → sincronizar FCX → esperar SyncDevice |
| Error MySQL `Can't connect` | MySQL no corriendo | `net start mysql` o iniciar servicio |

---

## Comandos útiles

```bash
# Sincronizar ahora
python manage.py sync_device

# Solo empleados (sin asistencia)
python manage.py sync_device --employees-only

# En JSON (para scripting)
python manage.py sync_device --json

# Shell de Django
python manage.py shell

# Migraciones
python manage.py makemigrations
python manage.py migrate
```

---

## Configuración del dispositivo

Valores actuales en `apps/attendance/pull.py`:

| Variable        | Valor          |
|-----------------|----------------|
| `DEVICE_IP`     | `10.10.0.3`    |
| `DEVICE_PORT`   | `4370`         |
| `DEVICE_PASSWORD` | `0`          |
| `TIMEOUT`       | `30` segundos  |

---

## Tecnologías

- **Backend**: Django 6, Python 3.14, MySQL 8
- **Frontend**: Bootstrap 5.3, Vanilla JS, CSS3
- **Dispositivo**: pyzk (librería ZK protocol), ZMM220_TFT
- **Scheduler**: Windows Scheduled Task (cada 1 minuto)
