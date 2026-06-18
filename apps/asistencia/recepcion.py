from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import RegistroAcceso
from .servicios import parsear_id
from apps.empleados.models import Empleado


@csrf_exempt
def cdata(request):
    if request.method == 'GET':
        return _manejar_get_cdata(request)
    elif request.method == 'POST':
        return _manejar_post_cdata(request)
    return HttpResponse(status=405)


def _manejar_get_cdata(request):
    sn = request.GET.get('SN', '')
    opciones = request.GET.get('options', '')

    if opciones == 'all':
        respuesta = (
            f"GET OPTION FROM: {sn}\r\n"
            f"ATTLOGStamp=0\r\n"
            f"OPERLOGStamp=0\r\n"
            f"Realtime=1\r\n"
            f"ServerVer=3.0.1\r\n"
            f"TransFlag=111111111111\r\n"
        )
        return HttpResponse(respuesta, content_type='text/plain')

    return HttpResponse('OK', content_type='text/plain')


def _manejar_post_cdata(request):
    tabla = request.GET.get('table', '')
    sn = request.GET.get('SN', '')
    cuerpo = request.body.decode('utf-8', errors='replace')

    if tabla == 'ATTLOG':
        _guardar_registros_asistencia(cuerpo, sn)

    return HttpResponse('OK', content_type='text/plain')


def _guardar_registros_asistencia(datos, sn):
    mapa_empleados = {e.id_numerico: e for e in Empleado.objects.all()}

    for linea in datos.strip().splitlines():
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

        emp = mapa_empleados.get(num)
        if not emp:
            continue

        try:
            marcado_en = datetime.strptime(cadena_fecha, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue

        marcado_en = timezone.make_aware(marcado_en)

        RegistroAcceso.objects.get_or_create(
            empleado=emp,
            marcado_en=marcado_en,
            defaults={
                'datos_originales': linea,
                'serial_dispositivo': sn,
            }
        )


@csrf_exempt
def obtener_solicitud(request):
    sn = request.GET.get('SN', '')
    ahora = timezone.localtime()

    respuesta = (
        f"GET OPTION FROM: {sn}\r\n"
        f"ATTLOGStamp={ahora.strftime('%Y-%m-%d %H:%M:%S')}\r\n"
        f"OPERLOGStamp={ahora.strftime('%Y-%m-%d %H:%M:%S')}\r\n"
        f"Realtime=1\r\n"
        f"ServerVer=3.0.1\r\n"
        f"TransFlag=111111111111\r\n"
    )

    return HttpResponse(respuesta, content_type='text/plain')
