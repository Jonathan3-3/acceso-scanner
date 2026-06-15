from django.urls import path
from . import views
from .push import cdata, getrequest

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.subir_archivo, name='subir-archivo'),
    path('api/report/', views.reporte_diario, name='reporte-diario'),
    path('api/sync-status/', views.estado_sincronizacion, name='estado-sincronizacion'),
    path('api/recent-scans/', views.registros_recientes, name='registros-recientes'),
    path('api/employees/', views.lista_empleados, name='lista-empleados'),
    path('api/employee/<int:pk>/detail/', views.detalle_empleado_api, name='detalle-empleado-api'),
    path('history/', views.historial, name='historial'),
    path('employee/<int:pk>/', views.detalle_empleado, name='detalle-empleado'),
    path('api/available-dates/', views.fechas_disponibles, name='fechas-disponibles'),
    path('api/scans-by-date/', views.registros_por_fecha, name='registros-por-fecha'),
    path('api/sync-device/', views.sincronizar_dispositivo, name='sincronizar-dispositivo'),
    path('iclock/cdata', cdata, name='push-cdata'),
    path('iclock/getrequest', getrequest, name='push-getrequest'),
]
