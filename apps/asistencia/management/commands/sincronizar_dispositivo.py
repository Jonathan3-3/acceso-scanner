import json
from django.core.management.base import BaseCommand
from ...extraccion import sincronizar_empleados, sincronizar_asistencia


class Command(BaseCommand):
    help = 'Sincroniza empleados y registros de asistencia desde el dispositivo FCX'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Salida en formato JSON',
        )
        parser.add_argument(
            '--solo-empleados',
            action='store_true',
            help='Solo sincronizar empleados, omitir asistencia',
        )

    def handle(self, *args, **options):
        self.stdout.write(f'Conectando al FCX ({self._info_dispositivo()})...')

        resultado_emp = sincronizar_empleados()
        if 'error' in resultado_emp:
            self.stderr.write(self.style.ERROR(
                f"Error sincronizando empleados: {resultado_emp['error']}"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Empleados: {resultado_emp['nuevos']} nuevos, "
                f"{resultado_emp['omitidos']} ya existentes"
            ))

        if options.get('solo_empleados'):
            if options['json']:
                self.stdout.write(json.dumps(resultado_emp, indent=2, ensure_ascii=False))
            return

        resultado_att = sincronizar_asistencia()

        if options['json']:
            salida = {'empleados': resultado_emp, 'asistencia': resultado_att}
            self.stdout.write(json.dumps(salida, indent=2, ensure_ascii=False))
            return

        if 'error' in resultado_att:
            self.stderr.write(self.style.ERROR(
                f"Error: {resultado_att['error']}"
            ))
            return

        self.stdout.write(self.style.SUCCESS(
            f"Asistencia: "
            f"{resultado_att['nuevos']} nuevos, "
            f"{resultado_att['omitidos']} ya existentes, "
            f"{resultado_att['no_emparejados']} sin empleado en BD"
        ))

        if resultado_att['nuevos'] > 0:
            self.stdout.write(f"Total en dispositivo: {resultado_att['total_dispositivo']}")

    def _info_dispositivo(self):
        from django.conf import settings
        return f"{settings.IP_DISPOSITIVO}:{settings.PUERTO_DISPOSITIVO}"
