from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import servicios_vendidos_view  

router = DefaultRouter()
router.register(r'proveedores', views.ProveedorViewSet)
router.register(r'categorias', views.CategoriaProductoViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'ventasreservas', views.VentaReservaViewSet)
router.register(r'pagos', views.PagoViewSet)
router.register(r'clientes', views.ClienteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('servicios-vendidos/', servicios_vendidos_view, name='servicios_vendidos'),
]
