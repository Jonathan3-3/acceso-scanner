from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Max
from django.utils import timezone
from datetime import date, datetime
from collections import defaultdict

from ..models import ScanRecord
from apps.employees.models import Employee


def registros_recientes(request):
    today_start = timezone.make_aware(datetime.combine(date.today(), datetime.min.time()))
    today_end = timezone.make_aware(datetime.combine(date.today(), datetime.max.time()))
    scans = ScanRecord.objects.filter(
        scanned_at__gte=today_start,
        scanned_at__lte=today_end,
    ).select_related('employee').order_by('-scanned_at')[:20]
    data = []
    for s in scans:
        tz = timezone.localtime(s.scanned_at)
        data.append({
            'id': s.employee.display_id,
            'employee_pk': s.employee.pk,
            'name': s.employee.name,
            'time': tz.strftime('%H:%M:%S'),
            'date': tz.strftime('%d/%m/%Y'),
            'device': s.device_sn,
        })
    return JsonResponse({'scans': data, 'total': len(data)})


def reporte_diario(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Fecha inválida'}, status=400)
    else:
        filter_date = date.today()

    day_start = timezone.make_aware(datetime.combine(filter_date, datetime.min.time()))
    day_end = timezone.make_aware(datetime.combine(filter_date, datetime.max.time()))

    scans = ScanRecord.objects.filter(
        scanned_at__gte=day_start,
        scanned_at__lte=day_end,
    ).select_related('employee')

    records = [(s.employee, s.scanned_at, s.raw_data) for s in scans]
    from ..services import calculate_report
    results, totals = calculate_report(records)

    return JsonResponse({
        'date': filter_date.isoformat(),
        'results': results,
        'totals': totals,
    })


def estado_sincronizacion(request):
    last_scan = ScanRecord.objects.aggregate(last=Max('scanned_at'))['last']
    last_sync = ScanRecord.objects.aggregate(last=Max('created_at'))['last']
    now = timezone.localtime()
    local_today = now.date()

    today_start = timezone.make_aware(datetime.combine(local_today, datetime.min.time()))
    today_end = timezone.make_aware(datetime.combine(local_today, datetime.max.time()))

    return JsonResponse({
        'device_ip': '10.10.0.3',
        'device_port': 4370,
        'last_scan': last_scan.isoformat() if last_scan else None,
        'last_sync': last_sync.isoformat() if last_sync else None,
        'server_time': now.isoformat(),
        'scans_today': ScanRecord.objects.filter(scanned_at__gte=today_start, scanned_at__lte=today_end).count(),
        'total_scans': ScanRecord.objects.count(),
        'total_employees': Employee.objects.count(),
    })


def lista_empleados(request):
    data = []
    for e in Employee.objects.all():
        data.append({
            'id': e.id,
            'display_id': e.display_id,
            'name': e.name,
        })
    return JsonResponse({'employees': data})


def detalle_empleado_api(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    try:
        if date_from:
            d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        else:
            d_from = date.today()
        if date_to:
            d_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            d_to = date.today()
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido. Use YYYY-MM-DD.'}, status=400)

    fromdatetime = timezone.make_aware(datetime.combine(d_from, datetime.min.time()))
    todatetime = timezone.make_aware(datetime.combine(d_to, datetime.max.time()))

    scans = ScanRecord.objects.filter(
        employee=employee,
        scanned_at__gte=fromdatetime,
        scanned_at__lte=todatetime,
    ).order_by('scanned_at').select_related('employee')

    local_today = timezone.localtime(timezone.now()).date()

    groups = defaultdict(list)
    for s in scans:
        local_dt = timezone.localtime(s.scanned_at)
        groups[local_dt.date()].append(local_dt)

    days = []
    total_seconds = 0
    for day in sorted(groups.keys()):
        times = sorted(groups[day])
        first = times[0]
        last = times[-1]

        is_today = day == local_today
        if is_today:
            secs = 0
            show_hours = None
            show_last = last.strftime('%H:%M:%S') if len(times) > 1 else '-'
        else:
            secs = (last - first).total_seconds()
            total_seconds += secs
            show_hours = round(secs / 3600, 2)
            show_last = last.strftime('%H:%M:%S')

        days.append({
            'date': day.isoformat(),
            'first_scan': first.strftime('%H:%M:%S'),
            'last_scan': show_last,
            'hours': show_hours,
        })

    total_hours = round(total_seconds / 3600, 2)
    avg_hours = round(total_hours / len(days), 2) if days else 0

    return JsonResponse({
        'employee': {
            'id': employee.id,
            'display_id': employee.display_id,
            'name': employee.name,
        },
        'date_from': d_from.isoformat(),
        'date_to': d_to.isoformat(),
        'days': days,
        'summary': {
            'total_days': len(days),
            'total_hours': total_hours,
            'avg_hours': avg_hours,
        },
    })


def registros_por_fecha(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Parámetro date requerido (YYYY-MM-DD)'}, status=400)
    try:
        filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Formato inválido. Use YYYY-MM-DD.'}, status=400)

    day_start = timezone.make_aware(datetime.combine(filter_date, datetime.min.time()))
    day_end = timezone.make_aware(datetime.combine(filter_date, datetime.max.time()))

    scans = ScanRecord.objects.filter(
        scanned_at__gte=day_start,
        scanned_at__lte=day_end,
    ).select_related('employee').order_by('scanned_at')

    data = []
    for s in scans:
        tz = timezone.localtime(s.scanned_at)
        data.append({
            'id': s.employee.display_id,
            'employee_pk': s.employee.pk,
            'name': s.employee.name,
            'time': tz.strftime('%H:%M:%S'),
            'date': tz.strftime('%d/%m/%Y'),
            'device': s.device_sn,
        })
    return JsonResponse({'scans': data, 'total': len(data), 'date': filter_date.isoformat()})


def sincronizar_dispositivo(request):
    from ..pull import sync_attendance, sync_employees

    resultado_empleados = sync_employees()
    resultado_asistencia = sync_attendance()

    return JsonResponse({
        'empleados': resultado_empleados,
        'asistencia': resultado_asistencia,
    })


def fechas_disponibles(request):
    dates = ScanRecord.objects.extra(
        select={'d': 'DATE(scanned_at)'}
    ).values_list('d', flat=True).distinct().order_by('-d')
    return JsonResponse({'dates': [d.isoformat() for d in dates if d is not None]})
