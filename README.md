# Control de Acceso — FCX (ZKTeco)

Sistema web Django para gestionar registros de asistencia del dispositivo **FCX** (ZMM220_TFT). Sincroniza automáticamente vía PULL (pyzk/TCP 4370), muestra entrada/salida por empleado por día y ofrece panel en tiempo real.

---

## Estructura del proyecto

```
acceso_scanner/
├── apps/
│   ├── asistencia/               # App de asistencia
│   │   ├── management/commands/
│   │   │   └── sincronizar_dispositivo.py
│   │   ├── migrations/
│   │   │   └── 0001_inicial.py
│   │   ├── models.py             # RegistroAcceso
│   │   ├── extraccion.py         # Sincronización PULL con pyzk
│   │   ├── recepcion.py          # Stubs PUSH (ZKTeco HTTP)
│   │   ├── servicios.py          # Lógica: reportes, matching, .DAT
│   │   ├── urls.py               # Rutas de la app
│   │   └── vistas/               # Panel, API, páginas
│   │       ├── api.py
│   │       ├── panel.py
│   │       └── paginas.py
│   ├── empleados/                # App de empleados
│   │   ├── migrations/
│   │   │   ├── 0001_inicial.py
│   │   │   └── 0002_cargar_empleados.py  # 27 empleados iniciales
│   │   └── models.py             # Empleado (id_original, nombre)
│   └── __init__.py
├── configuracion/                # Configuración Django
│   ├── ajustes.py                # MySQL, Timezone, dispositivo, STATICFILES_DIRS
│   ├── urls.py                   # Rutas raíz
│   └── wsgi.py                   # WSGI para producción
├── frontend/
│   ├── estatico/
│   │   ├── css/estilos.css       # Estilos (drop-zone, pulse, fade-in)
│   │   └── js/principal.js       # Lógica del panel (polling, upload)
│   └── plantillas/
│       ├── asistencia/
│       │   ├── panel.html        # Panel principal
│       │   ├── detalle_empleado.html
│       │   └── historial.html
│       └── base.html             # Layout base (Bootstrap 5 dark)
├── scripts/
│   ├── sincronizar_dispositivo.bat
│   ├── iniciar_servidor.ps1
│   ├── instalar_programacion.bat
│   └── instalar_programacion.ps1
├── registros/                    # Logs rotativos
├── manage.py
├── requisitos.txt
├── .env.ejemplo
└── backup_datos.json
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
pip install -r requisitos.txt
```

### 2. Crear base de datos MySQL

```sql
CREATE DATABASE acceso_scanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Las credenciales se configuran vía variables de entorno (ver `.env.ejemplo`):

| Variable     | Por defecto  |
|-------------|--------------|
| `DB_USUARIO` | root         |
| `DB_CLAVE`   | G@RR0M      |
| `DB_HOST`    | 127.0.0.1    |
| `DB_PUERTO`  | 3306         |

### 3. Migrar base de datos

```bash
python manage.py migrate
```

Esto crea las tablas y carga los **27 empleados** iniciales.

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

Abrir **http://localhost:8000/**.

### Sincronización manual con el FCX

```bash
python manage.py sincronizar_dispositivo
```

Conecta al dispositivo `10.10.0.3:4370`, descarga:
- **Empleados nuevos** (los crea en MySQL automáticamente)
- **Registros de asistencia nuevos** (los vincula al empleado correspondiente)

### Sincronización automática (cada 1 minuto)

Abrir PowerShell como **Administrador** y ejecutar:

```powershell
& "C:\Users\Jonathan Perez\acceso_scanner\scripts\instalar_programacion.bat"
```

Esto instala la tarea programada `SyncFCX` que corre cada minuto.

Para verificar:
```cmd
schtasks /query /tn SyncFCX
```

### Subir archivo .DAT manual

En el panel, arrastra un archivo .DAT (formato tab-separado: `AER0000142\t2024-08-26 07:16:30`) o haz clic para seleccionarlo. El sistema procesa, empareja empleados y muestra el reporte.

---

## API endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Panel HTML |
| GET | `/empleado/<pk>/` | Detalle HTML de un empleado |
| GET | `/historial/` | Historial HTML |
| GET | `/api/reporte/?fecha=YYYY-MM-DD` | Reporte diario (JSON) |
| GET | `/api/registros-recientes/` | Últimos 20 registros (JSON) |
| GET | `/api/estado-sincronizacion/` | Estado del dispositivo (JSON) |
| GET | `/api/empleados/` | Lista de empleados (JSON) |
| GET | `/api/empleado/<pk>/detalle/?desde=YYYY-MM-DD&hasta=YYYY-MM-DD` | Detalle por rango (JSON) |
| GET | `/api/fechas-disponibles/` | Fechas con registros |
| GET | `/api/registros-por-fecha/?fecha=YYYY-MM-DD` | Registros por fecha |
| GET | `/api/sincronizar-dispositivo/` | Sincronización manual vía API |
| POST | `/subir/` | Subir archivo .DAT (multipart) |
| POST | `/iclock/cdata` | PUSH ZKTeco |
| GET | `/iclock/getrequest` | PUSH ZKTeco |

### Ejemplo: detalle por empleado

```
GET /api/empleado/5/detalle/?desde=2026-06-01&hasta=2026-06-10
```

```json
{
  "empleado": { "id": 5, "id_visual": "AER149", "nombre": "FELIPE DE JESUS TAPIA GARCIA" },
  "fecha_desde": "2026-06-01",
  "fecha_hasta": "2026-06-10",
  "dias": [
    { "fecha": "2026-06-10", "entrada": "07:02:00", "salida": "17:30:00", "horas": 10.47 }
  ],
  "resumen": { "total_dias": 1, "total_horas": 10.47, "promedio_horas": 10.47 }
}
```

---

## Panel en vivo

- **Polling**: cada 5s consulta `/api/registros-recientes/` y muestra nuevos registros con badge **NUEVO**
- **Estadísticas**: cada 10s consulta `/api/estado-sincronizacion/`
- **Sincronización**: cada 1 minuto el comando `sincronizar_dispositivo` trae datos del FCX

---

## Flujo de datos

```
AccessPRO (app escritorio)
    ↓  (sincronización manual al dispositivo)
FCX (ZMM220_TFT)
    │  IP: 10.10.0.3  ·  Puerto: 4370  ·  Serial: AEYU194660027
    │
    ├── PULL → pyzk → SincronizarDispositivo (cada 1 min)
    │        ↓
    │   RegistroAcceso (MySQL)
    │        ↓
    │   Panel / API
    │
    └── PUSH → /iclock/cdata (implementado)
```

### Modelo de datos

```
Empleado                         RegistroAcceso
─────────                        ─────────────────
id (PK)                          id (PK)
id_original (unique)             empleado → Empleado (FK)
nombre                           marcado_en (datetime)
                                 datos_originales (text)
                                 serial_dispositivo (varchar)
                                 creado_en (datetime, auto)
```

- Cada `RegistroAcceso` es **una huella individual** del dispositivo
- El cálculo entrada/salida agrupa por `empleado + fecha`, toma `min(marcado_en)` y `max(marcado_en)`
- Los `id_visual` se formatean como `AER###` (ej. `AER142`)

---

## Mejoras implementadas en esta reestructuración

- ✅ **Código 100% en español**: variables, funciones, clases, constantes, API, URLs, templates, JS
- ✅ **Configuración centralizada**: IP, puerto, clave y serial del dispositivo en `configuracion/ajustes.py`
- ✅ **Variables de entorno**: secrets迁移 a `.env` (ver `.env.ejemplo`)
- ✅ **Bugs corregidos**: `extra()` → `TruncDate`, `transaction.atomic()` en sincronización, `get_or_create` evita duplicados
- ✅ **Código duplicado unificado**: `parsear_id` y `PATRON_ID` en un solo lugar (`servicios.py`)
- ✅ **Nombres Django obligatorios preservados**: `migrations/`, `management/commands/`, `models.py`, `apps.py`, `admin.py`
- ✅ **Scripts actualizados**: apuntan a `manage.py sincronizar_dispositivo`

---

## Solución de problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| `sincronizar_dispositivo` falla | Dispositivo no alcanzable | `ping 10.10.0.3` |
| Tarea SyncFCX no corre | Falta directorio | Usar `instalar_programacion.ps1` |
| Panel "Sin registros" | No sincronizado | `python manage.py sincronizar_dispositivo` |
| Error MySQL | MySQL no corriendo | `net start mysql` |

## Comandos útiles

```bash
python manage.py sincronizar_dispositivo
python manage.py sincronizar_dispositivo --solo-empleados
python manage.py sincronizar_dispositivo --json
python manage.py shell
python manage.py makemigrations
python manage.py migrate
```

## Configuración del dispositivo

Valores en `configuracion/ajustes.py` (sobrescribibles vía `.env`):

| Variable             | Valor          |
|----------------------|----------------|
| `IP_DISPOSITIVO`     | `10.10.0.3`    |
| `PUERTO_DISPOSITIVO` | `4370`         |
| `CLAVE_DISPOSITIVO`  | `0`            |
| `TIMEOUT_DISPOSITIVO`| `30` segundos  |
| `SERIAL_DISPOSITIVO` | `AEYU194660027`|

## Tecnologías

- **Backend**: Django 6.x, Python 3.14, MySQL 8
- **Frontend**: Bootstrap 5.3, Vanilla JS, CSS3
- **Dispositivo**: pyzk (protocolo ZK), ZMM220_TFT
- **Scheduler**: Windows Scheduled Task (cada 1 minuto)
