from django.db import models


class Empleado(models.Model):
    id_original = models.CharField(max_length=20, unique=True, verbose_name='ID original')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')

    class Meta:
        db_table = 'empleados'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.id_visual} - {self.nombre}"

    @property
    def id_visual(self):
        num_str = ''.join(c for c in self.id_original if c.isdigit())
        num = int(num_str) if num_str else 0
        return f"AER{num:03d}"

    @property
    def id_numerico(self):
        num_str = ''.join(c for c in self.id_original if c.isdigit())
        return int(num_str) if num_str else 0
