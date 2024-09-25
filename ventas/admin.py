from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, PrecioDinamico, Reserva, Venta

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
    list_display = ('producto', 'precio', 'fecha_inicio', 'fecha_fin')
    list_filter = ('producto',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cliente', 'fecha_reserva', 'cantidad')
    list_filter = ('producto', 'fecha_reserva')

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cliente', 'fecha_venta', 'cantidad', 'precio_total')
    list_filter = ('producto', 'fecha_venta')
    def precio_total(self, obj):
        return obj.precio_total

    precio_total.short_description = 'Precio Total'
    # precio_total.admin_order_field = 'precio_total'  # Uncomment if sortable