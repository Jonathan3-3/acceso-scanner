from django.db import models


class Employee(models.Model):
    raw_id = models.CharField(max_length=20, unique=True, verbose_name='ID original')
    name = models.CharField(max_length=200, verbose_name='Nombre')

    class Meta:
        db_table = 'empleados'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['name']

    def __str__(self):
        return f"{self.display_id} - {self.name}"

    @property
    def display_id(self):
        num_str = ''.join(c for c in self.raw_id if c.isdigit())
        num = int(num_str) if num_str else 0
        return f"AER{num:03d}"

    @property
    def numeric_id(self):
        num_str = ''.join(c for c in self.raw_id if c.isdigit())
        return int(num_str) if num_str else 0
