from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max
from django.utils import timezone
from datetime import datetime

from ..servicios import procesar_archivo_dat, emparejar_empleados, calcular_reporte, obtener_empleados_sin_registro
from ..models import RegistroAcceso
from apps.empleados.models import Empleado


def panel(request):
    hoy_local = timezone.localtime(timezone.now()).date()
    inicio_hoy = timezone.make_aware(datetime.combine(hoy_local, datetime.min.time()))
    fin_hoy = timezone.make_aware(datetime.combine(hoy_local, datetime.max.time()))

    ultimo_registro = RegistroAcceso.objects.aggregate(ultimo=Max('marcado_en'))['ultimo']
    ultima_sincro = RegistroAcceso.objects.aggregate(ultima=Max('creado_en'))['ultima']

    contexto = {
        'total_empleados': Empleado.objects.count(),
        'registros_hoy': RegistroAcceso.objects.filter(
            marcado_en__gte=inicio_hoy,
            marcado_en__lte=fin_hoy,
        ).count(),
        'total_registros': RegistroAcceso.objects.count(),
        'ultimo_registro': ultimo_registro,
        'ultima_sincronizacion': ultima_sincro,
        'ip_dispositivo': '10.10.0.3',
    }
    return render(request, 'asistencia/panel.html', contexto)


@csrf_exempt
def subir_archivo(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Usa POST'}, status=405)

    archivo = request.FILES.get('file')
    if not archivo:
        return JsonResponse({'error': 'No se recibió archivo'}, status=400)

    contenido = archivo.read().decode('utf-8', errors='replace')
    registros_crudos = procesar_archivo_dat(contenido)
    emparejados = emparejar_empleados(registros_crudos)

    if not emparejados:
        return JsonResponse({'error': 'No se encontraron registros válidos'}, status=400)

    for emp, dt, linea in emparejados:
        RegistroAcceso.objects.get_or_create(
            empleado=emp,
            marcado_en=dt,
            defaults={'datos_originales': linea, 'serial_dispositivo': 'upload'}
        )

    resultados, totales = calcular_reporte(emparejados)
    sin_registro = obtener_empleados_sin_registro(registros_crudos)

    return JsonResponse({
        'resultados': resultados,
        'totales': totales,
        'sin_registro': sin_registro,
        'total_empleados': len(totales),
        'total_registros': len(emparejados),
    })
