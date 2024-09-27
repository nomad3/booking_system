from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, PrecioDinamico, Reserva, Venta, Pago

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'es_externo')
    search_fields = ('nombre',)

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'cantidad_disponible', 'es_reservable', 'categoria', 'proveedor')
    search_fields = ('nombre',)
    list_filter = ('es_reservable', 'categoria', 'proveedor')

@admin.register(PrecioDinamico)
class PrecioDinamicoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'precio', 'fecha_inicio', 'fecha_fin', 'prioridad', 'dia_semana', 'mes')
    list_filter = ('producto', 'prioridad', 'dia_semana', 'mes')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cliente', 'fecha_reserva', 'cantidad')
    list_filter = ('producto', 'fecha_reserva')

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cliente', 'fecha_venta', 'cantidad', 'get_total')
    list_filter = ('producto', 'fecha_venta')

    def get_total(self, obj):
        return obj.total

    get_total.short_description = 'Total'
    get_total.admin_order_field = 'total'

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('venta', 'fecha_pago', 'monto', 'metodo_pago')
    list_filter = ('metodo_pago', 'fecha_pago')
