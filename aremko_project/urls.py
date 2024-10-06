from django.contrib import admin
from django.urls import path, include
from ventas.views import servicios_vendidos_view  
from .views import inicio_sistema_view  

urlpatterns = [
    path('', inicio_sistema_view, name='inicio_sistema'),  # Nueva vista de inicio
    path('servicios-vendidos/', servicios_vendidos_view, name='servicios_vendidos'),
    path('caja-diaria/', caja_diaria_view, name='caja_diaria'),  # Nueva vista de caja diaria
    path('auditoria-movimientos/', auditoria_movimientos_view, name='auditoria_movimientos'),  # Nueva vista de auditoría
    path('', include(router.urls)),  # Mantener las rutas del router
]
