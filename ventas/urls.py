from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear el router para las rutas automáticas de Django Rest Framework
router = DefaultRouter()

# Registrar las vistas con sus rutas
router.register(r'clientes', views.ClienteViewSet)
router.register(r'proveedores', views.ProveedorViewSet)
router.register(r'categorias', views.CategoriaProductoViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'ventasreservas', views.VentaReservaViewSet)  # Cambiado de 'ReservaViewSet' a 'VentaReservaViewSet'
router.register(r'pagos', views.PagoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
