from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('display_id', 'name', 'raw_id')
    search_fields = ('name', 'raw_id')
    ordering = ('name',)
