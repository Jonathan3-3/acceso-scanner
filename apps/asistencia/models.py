from django.db import models
from apps.empleados.models import Empleado


class RegistroAcceso(models.Model):
    empleado = models.ForeignKey(
        Empleado, on_delete=models.CASCADE,
        related_name='registros', verbose_name='Empleado'
    )
    marcado_en = models.DateTimeField(verbose_name='Fecha/Hora')
    datos_originales = models.TextField(blank=True, verbose_name='Línea original')
    serial_dispositivo = models.CharField(max_length=50, blank=True, verbose_name='Serial del dispositivo')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Recibido el')

    class Meta:
        db_table = 'registros_acceso'
        verbose_name = 'Registro de acceso'
        verbose_name_plural = 'Registros de acceso'
        ordering = ['-marcado_en']
        indexes = [
            models.Index(fields=['empleado', 'marcado_en']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['empleado', 'marcado_en'], name='unq_empleado_marcado_en'),
        ]

    def __str__(self):
        return f"{self.empleado.id_visual} @ {self.marcado_en}"
