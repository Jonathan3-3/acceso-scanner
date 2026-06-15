from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max
from django.utils import timezone
from datetime import datetime

from ..services import process_dat_file, match_employees, calculate_report, get_unmatched_employees
from ..models import ScanRecord
from apps.employees.models import Employee


def dashboard(request):
    local_today = timezone.localtime(timezone.now()).date()
    today_start = timezone.make_aware(datetime.combine(local_today, datetime.min.time()))
    today_end = timezone.make_aware(datetime.combine(local_today, datetime.max.time()))

    last_scan = ScanRecord.objects.aggregate(last=Max('scanned_at'))['last']
    last_sync = ScanRecord.objects.aggregate(last=Max('created_at'))['last']

    context = {
        'total_employees': Employee.objects.count(),
        'scans_today': ScanRecord.objects.filter(
            scanned_at__gte=today_start,
            scanned_at__lte=today_end,
        ).count(),
        'total_scans': ScanRecord.objects.count(),
        'last_scan': last_scan,
        'last_sync': last_sync,
        'device_ip': '10.10.0.3',
    }
    return render(request, 'attendance/dashboard.html', context)


@csrf_exempt
def subir_archivo(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Usa POST'}, status=405)

    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No se recibió archivo'}, status=400)

    raw = file.read().decode('utf-8', errors='replace')
    raw_records = process_dat_file(raw)
    matched = match_employees(raw_records)

    if not matched:
        return JsonResponse({'error': 'No se encontraron registros válidos'}, status=400)

    for emp, dt, line in matched:
        ScanRecord.objects.get_or_create(
            employee=emp,
            scanned_at=dt,
            defaults={'raw_data': line, 'device_sn': 'upload'}
        )

    results, totals = calculate_report(matched)
    unmatched = get_unmatched_employees(raw_records)

    return JsonResponse({
        'results': results,
        'totals': totals,
        'unmatched': unmatched,
        'total_employees': len(totals),
        'total_records': len(matched),
    })
