from django.db import models
from apps.employees.models import Employee


class ScanRecord(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE,
        related_name='scans', verbose_name='Empleado'
    )
    scanned_at = models.DateTimeField(verbose_name='Fecha/Hora')
    raw_data = models.TextField(blank=True, verbose_name='Línea original')
    device_sn = models.CharField(max_length=50, blank=True, verbose_name='Serial del dispositivo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Recibido el')

    class Meta:
        db_table = 'registros_acceso'
        verbose_name = 'Registro de acceso'
        verbose_name_plural = 'Registros de acceso'
        ordering = ['-scanned_at']
        indexes = [
            models.Index(fields=['employee', 'scanned_at']),
        ]

    def __str__(self):
        return f"{self.employee.display_id} @ {self.scanned_at}"
