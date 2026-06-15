from django.contrib import admin
from .models import ScanRecord


@admin.register(ScanRecord)
class ScanRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'scanned_at', 'device_sn')
    list_filter = ('scanned_at', 'device_sn')
    search_fields = ('employee__name', 'employee__raw_id')
    date_hierarchy = 'scanned_at'
