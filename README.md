# Control de Acceso — FCX (ZKTeco)

Sistema web Django para gestionar registros de asistencia del dispositivo **FCX** (ZMM220_TFT) en red local. Diseñado para **horas extra** y control de **comida**. Sincroniza vía PULL (pyzk/TCP 4370) cada hora y expone un proxy Apache con convivencia con apps PHP existentes.

---

## Estructura del proyecto

```
acceso_scanner/
├── apps/
│   ├── asistencia/                  # App de asistencia
│   │   ├── management/commands/
│   │   │   └── sincronizar_dispositivo.py
│   │   ├── migrations/
│   │   │   ├── 0001_inicial.py
│   │   │   └── 0002_renombrar_columnas.py
│   │   ├── models.py                # RegistroAcceso
│   │   ├── extraccion.py            # Sincronización PULL con pyzk
│   │   ├── recepcion.py             # Stubs PUSH (ZKTeco HTTP)
│   │   ├── servicios.py             # Lógica: reportes, matching, .DAT
│   │   ├── urls.py                  # Rutas de la app
│   │   └── vistas/
│   │       ├── api.py               # API endpoints + subir_archivo
│   │       └── paginas.py           # Views HTML: Principal, General, Hoy, Detalle
│   └── empleados/
│       ├── migrations/
│       │   ├── 0001_inicial.py
│       │   ├── 0002_cargar_empleados.py
│       │   └── 0003_renombrar_columnas.py
│       └── models.py                # Empleado (id_original, nombre)
├── configuracion/                   # Configuración Django
│   ├── ajustes.py                   # MySQL, Timezone, dispositivo, STATICFILES_DIRS
│   ├── urls.py                      # Rutas raíz (con prefijo /asistencia/)
│   └── wsgi.py                      # WSGI para producción
├── frontend/
│   ├── estatico/
│   │   ├── css/estilos.css
│   │   └── js/principal.js          # Polling, sync, stats en vivo
│   └── plantillas/
│       ├── base.html                # Layout base (Bootstrap 5 dark)
│       └── asistencia/
│           ├── principal.html       # Buscador + detalle individual
│           ├── general.html         # Todos empleados agrupados + Excel
│           ├── hoy.html             # Stats, polling, empleados
│           └── detalle_empleado.html # Detalle por empleado
├── registros/                       # Logs rotativos (django.log, sincronizacion.log)
├── scripts/                         # Instalación y sincronización
├── manage.py
├── requisitos.txt
├── .env.ejemplo
└── README.md
```

---

## Requisitos

- **Python** ≥ 3.10 (probado en 3.12)
- **MariaDB** 10.4+ / **MySQL** 8.0+ (base remota `luisen47_LGA`)
- **Dispositivo FCX** (ZMM220_TFT) en red local `10.10.0.237:4370`
- **Apache 2.4+** con mod_proxy, mod_rewrite (opcional para producción)

---

## Instalación

### 1. Clonar e instalar dependencias

```bash
cd acceso_scanner
pip install -r requisitos.txt
```

### 2. Configurar entorno

Copiar `.env.ejemplo` a `.env` y ajustar:

```env
DB_NOMBRE=luisen47_LGA
DB_USUARIO=tu_usuario
DB_CLAVE=tu_clave
DB_HOST=127.0.0.1
DB_PUERTO=3306
FCX_IP=10.10.0.237
FCX_PUERTO=4370
FCX_CLAVE=0
FCX_TIMEOUT=30
FCX_SERIAL=AEYU194660027
```

### 3. Migrar base de datos

```bash
python manage.py migrate
```

### 4. (Opcional) Cargar datos iniciales

```bash
python manage.py loaddata datos.json
```

---

## Uso

### Servidor de desarrollo

```bash
python manage.py runserver
```

Abrir **http://localhost:8000/asistencia/**.

### Páginas

- **`/asistencia/`** — Principal: buscar empleado por ID/nombre, ver detalle con filtros predefinidos (hoy, ayer, semana, mes) y exportar Excel individual.
- **`/asistencia/general/`** — General: rango semanal/mensual, tabla agrupada por empleado, exportar Excel general.
- **`/asistencia/hoy/`** — Hoy: stats en vivo, actividad reciente (polling 5s), empleados registrados.
- **`/asistencia/empleado/<pk>/`** — Detalle individual del empleado.

### Sincronización con el FCX

```bash
python manage.py sincronizar_dispositivo
```

Descarga empleados nuevos y registros de asistencia desde el dispositivo `10.10.0.237:4370`.

### Sincronización automática (cada hora)

En el servidor Windows, abrir PowerShell como **Administrador**:

```powershell
C:\Users\Usuario\Desktop\acceso_scanner\scripts\instalar_programacion.bat
```

Para verificar:

```cmd
schtasks /query /tn SyncFCX
```

---

## API endpoints

Todas las rutas deben accederse con prefijo `/asistencia/` cuando se usa Django directo. Con proxy Apache, el prefijo se maneja automáticamente.

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/asistencia/` | HTML Principal |
| GET | `/asistencia/general/` | HTML General |
| GET | `/asistencia/hoy/` | HTML Hoy |
| GET | `/asistencia/empleado/<pk>/` | HTML Detalle empleado |
| GET | `/asistencia/api/reporte/?desde=...&hasta=...` | Reporte por rango (JSON) |
| GET | `/asistencia/api/reporte/excel/?desde=...&hasta=...` | Exportar Excel |
| GET | `/asistencia/api/empleados/` | Lista empleados (JSON) |
| GET | `/asistencia/api/empleado/<pk>/detalle/?desde=...&hasta=...` | Detalle por rango (JSON) |
| GET | `/asistencia/api/registros-recientes/` | Últimos 20 registros (JSON) |
| GET | `/asistencia/api/estado-sincronizacion/` | Estado del dispositivo (JSON) |
| GET | `/asistencia/api/fechas-disponibles/` | Fechas con registros |
| GET | `/asistencia/api/sincronizar-dispositivo/` | Sincronización manual vía API |
| POST | `/asistencia/subir/` | Subir archivo .DAT (multipart) |
| POST | `/asistencia/iclock/cdata` | PUSH ZKTeco |
| GET | `/asistencia/iclock/getrequest` | PUSH ZKTeco |

---

## Producción (Apache proxy + Waitress)

### Servicio Windows (WinSW + Waitress)

El servicio `DjangoAcceso` corre `waitress-serve` en puerto `8000`.

```cmd
net start DjangoAcceso
net stop DjangoAcceso
```

### Configuración Apache (`httpd.conf`)

```apache
# Django proxy
ProxyPass /asistencia http://127.0.0.1:8000/asistencia
ProxyPassReverse /asistencia http://127.0.0.1:8000/asistencia
Alias /static C:/ruta/a/acceso_scanner/frontend/estatico
<Directory "C:/ruta/a/acceso_scanner/frontend/estatico">
    Require all granted
</Directory>
```

### Convivencia con apps PHP

Las apps PHP existentes (en `C:/xampp/htdocs/`) siguen en `/` sin cambios. Django vive bajo `/asistencia/` sin conflictos.

---

## Modelo de datos

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

- Cada `RegistroAcceso` es **una huella individual** del dispositivo.
- El cálculo entrada/salida agrupa por `empleado + fecha`, emparejando marcas consecutivas (pair grouping).
- `id_visual` se formatea como `AER###` (ej. `AER001`).
- Restricción única `(empleado, marcado_en)` evita duplicados.

---

## Flujo de datos

```
FCX (ZMM220_TFT)
    │  IP: 10.10.0.237  ·  Puerto: 4370  ·  Serial: AEYU194660027
    │
    ├── PULL → pyzk → sincronizar_dispositivo (cada 1 hora)
    │        ↓
    │   RegistroAcceso (MariaDB/MySQL)
    │        ↓
    │   API + Templates Django
    │
    └── PUSH → /iclock/cdata (implementado)
```

---

## Solución de problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| `sincronizar_dispositivo` falla | Dispositivo no alcanzable | `ping 10.10.0.237` |
| 404 en `/asistencia/` | Apache sin ProxyPass | Agregar regla en `httpd.conf` |
| "No tienes permisos" al navegar | Django genera `/` sin prefijo | Usar `FORCE_SCRIPT_NAME` o prefijo en `urls.py` |
| Error MySQL | MySQL no corriendo | `net start mysql` |
| Servicio no encuentra archivos | WinSW corrompido | Recargar `WinSW-x64.exe` |

---

## Tecnologías

- **Backend**: Django 4.2 LTS / 6.x, Python 3.x, MariaDB 10.4
- **Frontend**: Bootstrap 5.3 (dark), Vanilla JS, CSS3
- **Dispositivo**: pyzk (protocolo ZK), ZMM220_TFT
- **Producción**: Waitress, WinSW, Apache 2.4 (mod_proxy)
- **Scheduler**: Windows Scheduled Task (cada 1 hora)
