import re
from datetime import datetime
from collections import defaultdict
from django.utils import timezone
from apps.empleados.models import Empleado

PATRON_ID = re.compile(r'AER(\d+)', re.IGNORECASE)


def parsear_id(id_original):
    if not id_original:
        return None
    coincidencia = PATRON_ID.match(id_original.strip())
    if not coincidencia:
        return None
    return int(coincidencia.group(1))


def procesar_archivo_dat(contenido):
    lineas = contenido.strip().splitlines()
    registros_crudos = []

    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
        partes = linea.split('\t')
        if len(partes) < 2:
            continue

        id_original = partes[0].strip()
        cadena_fecha = partes[1].strip()

        num = parsear_id(id_original)
        if num is None:
            continue

        try:
            dt = datetime.strptime(cadena_fecha, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue

        registros_crudos.append((num, dt, linea))

    return registros_crudos


def emparejar_empleados(registros_crudos):
    empleados = {e.id_numerico: e for e in Empleado.objects.all()}
    emparejados = []
    for num, dt, linea in registros_crudos:
        emp = empleados.get(num)
        if emp:
            emparejados.append((emp, dt, linea))
    return emparejados


def convertir_local(dt):
    if dt.tzinfo is not None:
        return timezone.localtime(dt)
    return dt


TOLERANCIA_COMIDA_SEGS = 4200  # 1h10min


def _formatear_hms(dt):
    return dt.strftime('%H:%M:%S') if dt is not None else None


def _segundos_a_horas(segundos):
    return round(segundos / 3600, 2) if segundos is not None else None


def _incidencia_comida(c_horas_segs):
    if c_horas_segs is not None and c_horas_segs > TOLERANCIA_COMIDA_SEGS:
        return 'Excedió comida'
    return ''


def calcular_reporte(registros):
    grupos = defaultdict(list)

    for emp, dt, _ in registros:
        dt_local = convertir_local(dt)
        grupos[(emp.id, dt_local.date())].append(dt_local)

    resultados = []
    totales_jornada = defaultdict(float)
    totales_comida = defaultdict(float)
    fechas_empleado = defaultdict(set)
    hoy_local = timezone.localtime(timezone.now()).date()

    ids_empleados = {e[0] for e in grupos}
    mapa_empleados = {e.id: e for e in Empleado.objects.filter(id__in=ids_empleados)}

    for (emp_id, fecha), horas in grupos.items():
        horas.sort()
        empleado = mapa_empleados[emp_id]
        es_hoy = fecha == hoy_local
        n = len(horas)

        c_inicio = horas[0]
        c_fin = horas[1] if n >= 2 else None
        j_inicio = c_fin
        j_fin = horas[-1] if n >= 3 else None

        if n == 1:
            c_horas = None; c_segs = None; j_horas = None
        elif n == 2:
            c_segs = (c_fin - c_inicio).total_seconds()
            c_horas = _segundos_a_horas(c_segs)
            totales_comida[emp_id] += c_horas
            j_horas = None
        elif es_hoy:
            c_segs = (c_fin - c_inicio).total_seconds()
            c_horas = _segundos_a_horas(c_segs)
            totales_comida[emp_id] += c_horas
            j_horas = None
        else:
            c_segs = (c_fin - c_inicio).total_seconds()
            c_horas = _segundos_a_horas(c_segs)
            j_horas = _segundos_a_horas((j_fin - j_inicio).total_seconds())
            totales_comida[emp_id] += c_horas
            totales_jornada[emp_id] += j_horas

        resultados.append({
            'empleado_id': empleado.id_visual,
            'empleado_pk': empleado.pk,
            'nombre': empleado.nombre,
            'fecha': fecha.isoformat(),
            'comida_inicio': _formatear_hms(c_inicio),
            'comida_fin': _formatear_hms(c_fin),
            'comida_horas': c_horas,
            'jornada_inicio': _formatear_hms(j_inicio),
            'jornada_fin': _formatear_hms(j_fin),
            'jornada_horas': j_horas,
            'incidencia': _incidencia_comida(c_segs) if n >= 2 else '',
            'es_hoy': es_hoy,
            'n_marcas': n,
        })

        fechas_empleado[emp_id].add(fecha)

    todos_ids = set(totales_jornada.keys()) | set(totales_comida.keys())
    totales = []
    for emp_id in sorted(todos_ids):
        empleado = mapa_empleados[emp_id]
        totales.append({
            'empleado_id': empleado.id_visual,
            'empleado_pk': empleado.pk,
            'nombre': empleado.nombre,
            'dias': len(fechas_empleado[emp_id]),
            'fechas': sorted(f.isoformat() for f in fechas_empleado[emp_id]),
            'total_comida': round(totales_comida.get(emp_id, 0), 2),
            'total_jornada': round(totales_jornada.get(emp_id, 0), 2),
        })

    return resultados, totales


def obtener_empleados_sin_registro(registros_crudos):
    numeros_escaneados = set(num for num, _, _ in registros_crudos)
    sin_registro = []
    for emp in Empleado.objects.all():
        if emp.id_numerico not in numeros_escaneados:
            sin_registro.append({
                'id': emp.id_visual,
                'nombre': emp.nombre,
            })
    return sin_registro
