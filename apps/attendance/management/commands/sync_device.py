import json
from django.core.management.base import BaseCommand
from apps.attendance.pull import sync_employees, sync_attendance


class Command(BaseCommand):
    help = 'Sincroniza empleados y registros de asistencia desde el dispositivo FCX'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Salida en formato JSON',
        )
        parser.add_argument(
            '--employees-only',
            action='store_true',
            help='Solo sincronizar empleados, omitir asistencia',
        )

    def handle(self, *args, **options):
        self.stdout.write('Conectando al FCX (10.10.0.3:4370)...')

        emp_result = sync_employees()
        if 'error' in emp_result:
            self.stderr.write(self.style.ERROR(f"Error sincronizando empleados: {emp_result['error']}"))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Empleados: {emp_result['new']} nuevos, "
                f"{emp_result['skipped']} ya existentes"
            ))

        if options['employees_only']:
            if options['json']:
                self.stdout.write(json.dumps(emp_result, indent=2))
            return

        att_result = sync_attendance()

        if options['json']:
            output = {'employees': emp_result, 'attendance': att_result}
            self.stdout.write(json.dumps(output, indent=2))
            return

        if 'error' in att_result:
            self.stderr.write(self.style.ERROR(f"Error: {att_result['error']}"))
            return

        self.stdout.write(self.style.SUCCESS(
            f"Asistencia: "
            f"{att_result['new']} nuevos, "
            f"{att_result['skipped']} ya existentes, "
            f"{att_result['unmatched']} sin empleado en DB"
        ))

        if att_result['new'] > 0:
            self.stdout.write(f"Total en dispositivo: {att_result['total_device']}")
