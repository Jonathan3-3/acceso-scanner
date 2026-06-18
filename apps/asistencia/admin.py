from django.contrib import admin
from .models import RegistroAcceso


@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'marcado_en', 'serial_dispositivo')
    list_filter = ('marcado_en', 'serial_dispositivo')
    search_fields = ('empleado__nombre', 'empleado__id_original')
    date_hierarchy = 'marcado_en'
