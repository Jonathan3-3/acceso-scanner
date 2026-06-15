import re
from datetime import datetime, date
from collections import defaultdict
from django.utils import timezone
from .models import ScanRecord
from apps.employees.models import Employee


ID_PATTERN = re.compile(r'AER(\d+)', re.IGNORECASE)


def parse_id(raw_id):
    match = ID_PATTERN.match(raw_id.strip())
    if not match:
        return None
    return int(match.group(1))


def process_dat_file(file_content):
    lines = file_content.strip().splitlines()
    raw_records = []

    for line in lines:
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

        try:
            dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue

        raw_records.append((num, dt, line))

    return raw_records


def match_employees(raw_records):
    employees = {e.numeric_id: e for e in Employee.objects.all()}
    matched = []
    for num, dt, line in raw_records:
        emp = employees.get(num)
        if emp:
            matched.append((emp, dt, line))
    return matched


def calculate_report(records):
    groups = defaultdict(list)

    def to_local(dt):
        if dt.tzinfo is not None:
            return timezone.localtime(dt)
        return dt

    for emp, dt, _ in records:
        local_dt = to_local(dt)
        groups[(emp.id, local_dt.date())].append(local_dt)

    results = []
    employee_totals = defaultdict(float)
    employee_dates = defaultdict(set)
    local_today = timezone.localtime(timezone.now()).date()

    for (emp_id, date_key), times in groups.items():
        times.sort()
        first = times[0]
        last = times[-1]
        emp = Employee.objects.get(id=emp_id)

        is_today = date_key == local_today
        if is_today:
            hours = None
        else:
            hours = round((last - first).total_seconds() / 3600, 2)
            employee_totals[emp_id] += hours

        results.append({
            'num': emp.numeric_id,
            'id': emp.display_id,
            'pk': emp.pk,
            'name': emp.name,
            'date': date_key.isoformat(),
            'first_scan': first.strftime('%H:%M:%S'),
            'last_scan': last.strftime('%H:%M:%S'),
            'hours': hours,
        })

        employee_dates[emp_id].add(date_key)

    totals = []
    for emp_id, total_hours in sorted(employee_totals.items()):
        emp = Employee.objects.get(id=emp_id)
        totals.append({
            'id': emp.display_id,
            'pk': emp.pk,
            'name': emp.name,
            'days': len(employee_dates[emp_id]),
            'dates': sorted(d.isoformat() for d in employee_dates[emp_id]),
            'total_hours': round(total_hours, 2),
        })

    return results, totals


def get_unmatched_employees(raw_records):
    scanned_nums = set(num for num, _, _ in raw_records)
    unmatched = []
    for emp in Employee.objects.all():
        if emp.numeric_id not in scanned_nums:
            unmatched.append({
                'id': emp.display_id,
                'name': emp.name,
            })
    return unmatched
