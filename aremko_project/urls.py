from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ventas.urls')),
    path('servicios-vendidos/', servicios_vendidos_view, name='servicios_vendidos'),

]
