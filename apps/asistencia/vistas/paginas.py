from django.shortcuts import render, get_object_or_404
from django.db.models import Max
from django.utils import timezone
from apps.empleados.models import Empleado
from ..models import RegistroAcceso


def detalle_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    return render(request, 'asistencia/detalle_empleado.html', {
        'empleado': empleado,
    })


def principal(request):
    return render(request, 'asistencia/principal.html')


def general(request):
    return render(request, 'asistencia/general.html')


def hoy(request):
    empleados = Empleado.objects.count()
    ultimo = RegistroAcceso.objects.aggregate(ultimo=Max('marcado_en'))['ultimo']
    ultima_sincro = RegistroAcceso.objects.aggregate(ultima=Max('creado_en'))['ultima']
    hoy_local = timezone.localtime(timezone.now()).date()
    inicio_hoy = timezone.make_aware(timezone.datetime.combine(hoy_local, timezone.datetime.min.time()))
    fin_hoy = timezone.make_aware(timezone.datetime.combine(hoy_local, timezone.datetime.max.time()))
    registros_hoy = RegistroAcceso.objects.filter(
        marcado_en__gte=inicio_hoy, marcado_en__lte=fin_hoy
    ).count()
    return render(request, 'asistencia/hoy.html', {
        'total_empleados': empleados,
        'total_registros': RegistroAcceso.objects.count(),
        'registros_hoy': registros_hoy,
        'ultimo_registro': ultimo,
        'ultima_sincronizacion': ultima_sincro,
    })
