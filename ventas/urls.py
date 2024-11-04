from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'proveedores', views.ProveedorViewSet)
router.register(r'categorias', views.CategoriaProductoViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'ventasreservas', views.VentaReservaViewSet)
router.register(r'pagos', views.PagoViewSet)
router.register(r'clientes', views.ClienteViewSet)

urlpatterns = [
    path('', views.inicio_sistema_view, name='inicio_sistema'),
    path('servicios-vendidos/', views.servicios_vendidos_view, name='servicios_vendidos'),
    path('servicios-vendidos/actualizar-estado/<int:servicio_id>/', views.actualizar_estado_servicio, name='actualizar_estado_servicio'),
    path('caja-diaria/', views.caja_diaria_view, name='caja_diaria'),
    path('auditoria-movimientos/', views.auditoria_movimientos_view, name='auditoria_movimientos'),
    path('', include(router.urls)),
    path('venta_reservas/', views.venta_reserva_list, name='venta_reserva_list'),
    path('venta_reservas/<int:pk>/', views.venta_reserva_detail, name='venta_reserva_detail'),
]
