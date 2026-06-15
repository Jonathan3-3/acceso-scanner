import re
import logging

from django.utils import timezone

from apps.employees.models import Employee
from .models import ScanRecord

logger = logging.getLogger(__name__)

DEVICE_IP = '10.10.0.3'
DEVICE_PORT = 4370
DEVICE_PASSWORD = 0
TIMEOUT = 30

ID_PATTERN = re.compile(r'AER(\d+)', re.IGNORECASE)


def _parse_id(raw):
    match = ID_PATTERN.match(raw.strip())
    if not match:
        return None
    return int(match.group(1))


def sync_employees():
    from zk import ZK

    zk = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=TIMEOUT, password=DEVICE_PASSWORD)
    device = None

    try:
        logger.info(f"Conectando a {DEVICE_IP}:{DEVICE_PORT} para sincronizar empleados...")
        device = zk.connect()
        users = device.get_users()
        logger.info(f"Empleados obtenidos del dispositivo: {len(users)}")

        existing = {e.numeric_id for e in Employee.objects.all()}
        created = 0
        skipped = 0

        for user in users:
            uid = str(user.user_id).strip()
            match = ID_PATTERN.match(uid)
            if not match:
                skipped += 1
                continue

            num = int(match.group(1))
            if num in existing:
                skipped += 1
                continue

            raw_id = f"AER{num:07d}"
            name = user.name.strip() if (user.name and user.name.strip()) else f"EMPLEADO {uid}"
            Employee.objects.create(raw_id=raw_id, name=name)
            existing.add(num)
            created += 1

        logger.info(f"Empleados sincronizados: {created} nuevos, {skipped} ya existentes")
        return {'new': created, 'skipped': skipped, 'total_device': len(users)}

    except Exception as e:
        logger.error(f"Error sincronizando empleados: {e}")
        return {'error': str(e)}

    finally:
        if device:
            try:
                device.disconnect()
            except Exception:
                pass
        try:
            zk.disconnect()
        except Exception:
            pass


def sync_attendance():
    from zk import ZK

    zk = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=TIMEOUT, password=DEVICE_PASSWORD)
    device = None

    try:
        logger.info(f"Conectando a {DEVICE_IP}:{DEVICE_PORT}...")
        device = zk.connect()
        logger.info("Conectado. Obteniendo registros de asistencia...")

        attendance = device.get_attendance()
        logger.info(f"Registros obtenidos del dispositivo: {len(attendance)}")

        employees_map = {e.numeric_id: e for e in Employee.objects.all()}
        known = set(
            ScanRecord.objects.values_list('employee_id', 'scanned_at')
        )

        new_count = 0
        skipped_count = 0
        unmatched_count = 0

        for att in attendance:
            user_num = _parse_id(str(att.user_id))
            if user_num is None:
                unmatched_count += 1
                continue

            emp = employees_map.get(user_num)
            if not emp:
                unmatched_count += 1
                continue

            ts = att.timestamp
            if ts.tzinfo is None:
                ts = timezone.make_aware(ts)

            if (emp.id, ts) in known:
                skipped_count += 1
                continue

            ScanRecord.objects.create(
                employee=emp,
                scanned_at=ts,
                raw_data=(
                    f"PULL:{att.user_id}\t"
                    f"{ts.strftime('%Y-%m-%d %H:%M:%S')}\t"
                    f"{att.status}"
                ),
                device_sn='AEYU194660027',
            )
            new_count += 1

        logger.info(
            f"Sincronización completada: "
            f"{new_count} nuevos, {skipped_count} ya existentes, "
            f"{unmatched_count} sin empleado en DB"
        )

        return {
            'new': new_count,
            'skipped': skipped_count,
            'unmatched': unmatched_count,
            'total_device': len(attendance),
        }

    except Exception as e:
        logger.error(f"Error sincronizando dispositivo: {e}")
        return {'error': str(e)}

    finally:
        if device:
            try:
                device.disconnect()
            except Exception:
                pass
        try:
            zk.disconnect()
        except Exception:
            pass
