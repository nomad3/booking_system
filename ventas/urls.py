from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'proveedores', views.ProveedorViewSet)
router.register(r'categorias', views.CategoriaProductoViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'reservas', views.ReservaViewSet)
router.register(r'ventas', views.VentaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('manychat/', views.manychat_webhook),
    path('manychat/chatgpt/', views.manychat_chatgpt_webhook),  # Nuevo endpoint
]
