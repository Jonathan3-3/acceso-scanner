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


def calcular_reporte(registros):
    grupos = defaultdict(list)

    for emp, dt, _ in registros:
        dt_local = convertir_local(dt)
        grupos[(emp.id, dt_local.date())].append(dt_local)

    resultados = []
    totales_empleado = defaultdict(float)
    fechas_empleado = defaultdict(set)
    hoy_local = timezone.localtime(timezone.now()).date()

    ids_empleados = {e[0] for e in grupos}
    mapa_empleados = {e.id: e for e in Empleado.objects.filter(id__in=ids_empleados)}

    for (emp_id, fecha), horas in grupos.items():
        horas.sort()
        primera = horas[0]
        ultima = horas[-1]
        empleado = mapa_empleados[emp_id]

        es_hoy = fecha == hoy_local
        if es_hoy:
            total_horas = None
        else:
            total_horas = round((ultima - primera).total_seconds() / 3600, 2)
            totales_empleado[emp_id] += total_horas

        resultados.append({
            'empleado_id': empleado.id_visual,
            'empleado_pk': empleado.pk,
            'nombre': empleado.nombre,
            'fecha': fecha.isoformat(),
            'entrada': primera.strftime('%H:%M:%S'),
            'salida': ultima.strftime('%H:%M:%S'),
            'horas': total_horas,
        })

        fechas_empleado[emp_id].add(fecha)

    totales = []
    for emp_id, total_horas in sorted(totales_empleado.items()):
        empleado = mapa_empleados[emp_id]
        totales.append({
            'empleado_id': empleado.id_visual,
            'empleado_pk': empleado.pk,
            'nombre': empleado.nombre,
            'dias': len(fechas_empleado[emp_id]),
            'fechas': sorted(d.isoformat() for d in fechas_empleado[emp_id]),
            'total_horas': round(total_horas, 2),
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
