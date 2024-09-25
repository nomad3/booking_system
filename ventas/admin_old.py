from django.contrib import admin
from .models import Cliente, Habitacion, Masaje, TinaCaliente, Producto, Venta, Reserva, PrecioDinamico

# Clase para la gestión de precios dinámicos
class PrecioDinamicoAdmin(admin.ModelAdmin):
    list_display = ('objeto', 'incremento_dia_semana', 'incremento_hora_dia', 'incremento_mes')

# Clase para gestionar habitaciones
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'precio_base')

# Clase para gestionar masajes
class MasajeAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'duracion', 'precio_base')

# Clase para gestionar tinas calientes
class TinaCalienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'precio_base')

# Clase para gestionar productos
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'stock', 'precio_fijo')
    search_fields = ['nombre']
    list_filter = ['stock']

# Clase para gestionar ventas (pedidos)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'total')
    search_fields = ['fecha']
    list_filter = ['fecha']
    filter_horizontal = ('productos_vendidos',)  # Para seleccionar productos en la venta

# Clase para gestionar reservas
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'fecha_inicio', 'fecha_fin', 'total')
    search_fields = ['cliente__nombre', 'fecha_inicio']
    list_filter = ['fecha_inicio']
    filter_horizontal = ('habitacion', 'masaje', 'tina_caliente')  # Para seleccionar productos relacionados

# Registrar los modelos en el panel de administración
admin.site.register(Cliente)
admin.site.register(Habitacion, HabitacionAdmin)
admin.site.register(Masaje, MasajeAdmin)
admin.site.register(TinaCaliente, TinaCalienteAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Venta, VentaAdmin)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(PrecioDinamico, PrecioDinamicoAdmin)
