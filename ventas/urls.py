from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ventas'

# Registrar las vistas en el router de DRF
router = DefaultRouter()
router.register(r'proveedores', views.ProveedorViewSet)
router.register(r'categorias', views.CategoriaProductoViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'ventasreservas', views.VentaReservaViewSet)
router.register(r'pagos', views.PagoViewSet)
router.register(r'clientes', views.ClienteViewSet)

# Añadir las nuevas vistas a las URLs
urlpatterns = [
    path('servicios-vendidos/', views.servicios_vendidos_view, name='servicios_vendidos'),
    path('caja-diaria/', views.caja_diaria_view, name='caja_diaria'),
    path('auditoria-movimientos/', views.auditoria_movimientos_view, name='auditoria_movimientos'),
    path('venta_reservas/', views.venta_reserva_list, name='venta_reserva_list'),
    path('venta_reservas/<int:pk>/', views.venta_reserva_detail, name='venta_reserva_detail'),
    path('api/', include(router.urls)),
]
