from django.contrib import admin
from django.urls import path, include
from ventas.views import servicios_vendidos_view
from ventas.views import inicio_sistema_view
from ventas.views import caja_diaria_view
from ventas.views import auditoria_movimientos_view, venta_reserva_list, venta_reserva_detail

urlpatterns = [
    path('admin/', admin.site.urls),  # Esta línea es clave para registrar el namespace 'admin'
    path('', inicio_sistema_view, name='inicio_sistema'),  # Nueva vista de inicio
    path('ventas/', venta_reserva_list, name='venta_reserva_list'),
    path('servicios-vendidos/', servicios_vendidos_view, name='servicios_vendidos'),
    path('caja-diaria/', caja_diaria_view, name='caja_diaria'),  # Nueva vista de caja diaria
    path('auditoria-movimientos/', auditoria_movimientos_view, name='auditoria_movimientos'),  # Nueva vista de auditoría
    path('ventas/<int:pk>/', venta_reserva_detail, name='venta_reserva_detail'),
]
