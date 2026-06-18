import logging
import time
from datetime import datetime

from django.conf import settings
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from apps.empleados.models import Empleado
from .models import RegistroAcceso
from .servicios import parsear_id

logger = logging.getLogger(__name__)


def sincronizar_empleados():
    from zk import ZK

    zk = ZK(
        settings.IP_DISPOSITIVO,
        port=settings.PUERTO_DISPOSITIVO,
        timeout=settings.TIMEOUT_DISPOSITIVO,
        password=settings.CLAVE_DISPOSITIVO
    )
    dispositivo = None

    try:
        logger.info(f"Conectando a {settings.IP_DISPOSITIVO}:{settings.PUERTO_DISPOSITIVO} para sincronizar empleados...")
        dispositivo = zk.connect()
        usuarios = dispositivo.get_users()
        logger.info(f"Empleados obtenidos del dispositivo: {len(usuarios)}")

        existentes = {e.id_numerico for e in Empleado.objects.all()}
        creados = 0
        omitidos = 0

        for usuario in usuarios:
            uid = str(usuario.user_id).strip()
            num = parsear_id(uid)
            if num is None:
                omitidos += 1
                continue

            if num in existentes:
                omitidos += 1
                continue

            id_original = f"AER{num:07d}"
            nombre = usuario.name.strip() if (usuario.name and usuario.name.strip()) else f"EMPLEADO {uid}"
            Empleado.objects.create(id_original=id_original, nombre=nombre)
            existentes.add(num)
            creados += 1

        logger.info(f"Empleados sincronizados: {creados} nuevos, {omitidos} ya existentes")
        return {'nuevos': creados, 'omitidos': omitidos, 'total_dispositivo': len(usuarios)}

    except Exception as e:
        logger.error(f"Error sincronizando empleados: {e}")
        return {'error': str(e)}

    finally:
        if dispositivo:
            try:
                dispositivo.disconnect()
            except Exception:
                pass
        try:
            zk.disconnect()
        except Exception:
            pass


def sincronizar_asistencia():
    from zk import ZK

    ultimo_registro = RegistroAcceso.objects.aggregate(ultimo=Max('marcado_en'))['ultimo']
    ventana = (
        ultimo_registro - timezone.timedelta(hours=1)
        if ultimo_registro
        else timezone.make_aware(datetime(2000, 1, 1))
    )

    for intento in range(3):
        zk = ZK(
            settings.IP_DISPOSITIVO,
            port=settings.PUERTO_DISPOSITIVO,
            timeout=settings.TIMEOUT_DISPOSITIVO,
            password=settings.CLAVE_DISPOSITIVO
        )
        dispositivo = None
        try:
            logger.info(f"Conectando a {settings.IP_DISPOSITIVO}:{settings.PUERTO_DISPOSITIVO} (intento {intento+1}/3)...")
            dispositivo = zk.connect()
            logger.info("Conectado. Obteniendo registros de asistencia...")
            registros = dispositivo.get_attendance()
            logger.info(f"Registros obtenidos del dispositivo: {len(registros)}")
            break
        except Exception as e:
            logger.warning(f"Intento {intento+1} falló: {e}")
            if dispositivo:
                try:
                    dispositivo.disconnect()
                except Exception:
                    pass
            try:
                zk.disconnect()
            except Exception:
                pass
            if intento == 2:
                return {'error': str(e)}
            time.sleep(2 ** intento)
            continue

    mapa_empleados = {e.id_numerico: e for e in Empleado.objects.all()}
    conocidos = set(
        RegistroAcceso.objects.filter(marcado_en__gte=ventana)
        .values_list('empleado_id', 'marcado_en')
    )

    nuevos = 0
    omitidos = 0
    no_emparejados = 0

    with transaction.atomic():
        for att in registros:
            num_usuario = parsear_id(str(att.user_id))
            if num_usuario is None:
                no_emparejados += 1
                continue

            emp = mapa_empleados.get(num_usuario)
            if not emp:
                no_emparejados += 1
                continue

            ts = att.timestamp
            if ts.tzinfo is None:
                ts = timezone.make_aware(ts)

            if ts < ventana:
                omitidos += 1
                continue

            if (emp.id, ts) in conocidos:
                omitidos += 1
                continue

            _, creado = RegistroAcceso.objects.get_or_create(
                empleado=emp,
                marcado_en=ts,
                defaults={
                    'datos_originales': (
                        f"PULL:{att.user_id}\t"
                        f"{ts.strftime('%Y-%m-%d %H:%M:%S')}\t"
                        f"{att.status}"
                    ),
                    'serial_dispositivo': settings.SERIAL_DISPOSITIVO,
                }
            )
            if creado:
                nuevos += 1
            else:
                omitidos += 1

    logger.info(
        f"Sincronización completada: "
        f"{nuevos} nuevos, {omitidos} ya existentes, "
        f"{no_emparejados} sin empleado en BD"
    )

    if dispositivo:
        try:
            dispositivo.disconnect()
        except Exception:
            pass
    try:
        zk.disconnect()
    except Exception:
        pass

    return {
        'nuevos': nuevos,
        'omitidos': omitidos,
        'no_emparejados': no_emparejados,
        'total_dispositivo': len(registros),
    }
