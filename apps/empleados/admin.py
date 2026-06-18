from django.contrib import admin
from .models import Empleado


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('id_visual', 'nombre', 'id_original')
    search_fields = ('nombre', 'id_original')
    ordering = ('nombre',)
