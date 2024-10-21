from django.contrib import admin
from django.urls import path, include
from ventas.views import inicio_sistema_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio_sistema_view, name='inicio_sistema'),
    path('ventas/', include(('ventas.urls', 'ventas'), namespace='ventas')),
]
