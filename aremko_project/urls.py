from django.contrib import admin
from django.urls import path, include
from ventas.views import servicios_vendidos_view  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('servicios-vendidos/', servicios_vendidos_view, name='servicios_vendidos'),  # Asegúrate de que esté aquí
    path('api/', include('ventas.urls')),  # Incluye las rutas de la aplicación ventas
]
