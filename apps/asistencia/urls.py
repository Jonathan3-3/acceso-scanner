from django.urls import path
from . import vistas
from .recepcion import cdata, obtener_solicitud

urlpatterns = [
    path('', vistas.principal, name='principal'),
    path('general/', vistas.general, name='general'),
    path('hoy/', vistas.hoy, name='hoy'),
    path('subir/', vistas.subir_archivo, name='subir-archivo'),
    path('api/reporte/', vistas.reporte_diario, name='reporte-diario'),
    path('api/reporte/excel/', vistas.exportar_reporte_excel, name='reporte-excel'),
    path('api/estado-sincronizacion/', vistas.estado_sincronizacion, name='estado-sincronizacion'),
    path('api/registros-recientes/', vistas.registros_recientes, name='registros-recientes'),
    path('api/empleados/', vistas.lista_empleados, name='lista-empleados'),
    path('api/empleado/<int:pk>/detalle/', vistas.detalle_empleado_api, name='detalle-empleado-api'),
    path('empleado/<int:pk>/', vistas.detalle_empleado, name='detalle-empleado'),
    path('api/fechas-disponibles/', vistas.fechas_disponibles, name='fechas-disponibles'),
    path('api/registros-por-fecha/', vistas.registros_por_fecha, name='registros-por-fecha'),
    path('api/sincronizar-dispositivo/', vistas.sincronizar_dispositivo, name='sincronizar-dispositivo'),
    path('iclock/cdata', cdata, name='push-cdata'),
    path('iclock/getrequest', obtener_solicitud, name='push-getrequest'),
]
