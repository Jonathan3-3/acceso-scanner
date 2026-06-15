"""
Handlers for the ZKTeco PUSH communication protocol.
The device sends attendance data via HTTP POST to /iclock/cdata.
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime
from .models import ScanRecord
from .services import parse_id
from apps.employees.models import Employee


@csrf_exempt
def cdata(request):
    if request.method == 'GET':
        return _handle_get_cdata(request)
    elif request.method == 'POST':
        return _handle_post_cdata(request)
    return HttpResponse(status=405)


def _handle_get_cdata(request):
    sn = request.GET.get('SN', '')
    options = request.GET.get('options', '')

    if options == 'all':
        response = (
            f"GET OPTION FROM: {sn}\r\n"
            f"ATTLOGStamp=0\r\n"
            f"OPERLOGStamp=0\r\n"
            f"Realtime=1\r\n"
            f"ServerVer=3.0.1\r\n"
            f"TransFlag=111111111111\r\n"
        )
        return HttpResponse(response, content_type='text/plain')

    return HttpResponse('OK', content_type='text/plain')


def _handle_post_cdata(request):
    table = request.GET.get('table', '')
    sn = request.GET.get('SN', '')
    body = request.body.decode('utf-8', errors='replace')

    if table == 'ATTLOG':
        _save_attendance_logs(body, sn)

    return HttpResponse('OK', content_type='text/plain')


def _save_attendance_logs(data, sn):
    employee_map = {e.numeric_id: e for e in Employee.objects.all()}

    for line in data.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            continue

        raw_id = parts[0].strip()
        dt_str = parts[1].strip()

        num = parse_id(raw_id)
        if num is None:
            continue

        emp = employee_map.get(num)
        if not emp:
            continue

        try:
            scanned_at = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue

        scanned_at = timezone.make_aware(scanned_at)

        ScanRecord.objects.get_or_create(
            employee=emp,
            scanned_at=scanned_at,
            defaults={
                'raw_data': line,
                'device_sn': sn,
            }
        )


@csrf_exempt
def getrequest(request):
    sn = request.GET.get('SN', '')
    now = timezone.localtime()

    response = (
        f"GET OPTION FROM: {sn}\r\n"
        f"ATTLOGStamp={now.strftime('%Y-%m-%d %H:%M:%S')}\r\n"
        f"OPERLOGStamp={now.strftime('%Y-%m-%d %H:%M:%S')}\r\n"
        f"Realtime=1\r\n"
        f"ServerVer=3.0.1\r\n"
        f"TransFlag=111111111111\r\n"
    )

    return HttpResponse(response, content_type='text/plain')
