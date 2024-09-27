# ventas/admin.py

from django.contrib import admin
from .models import (
    Cliente,
    Venta,
    MovimientoCliente,
    Producto,
    CategoriaProducto,
    Proveedor,
    Reserva,
    PrecioDinamico,
    Pago
)

class MovimientoClienteInline(admin.TabularInline):
    model = MovimientoCliente
    extra = 0
    readonly_fields = ('tipo_movimiento', 'descripcion', 'fecha')
    can_delete = False
    show_change_link = False

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo_electronico', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'correo_electronico')
    list_filter = ('fecha_registro',)
    inlines = [MovimientoClienteInline]

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cliente', 'fecha_venta', 'cantidad', 'get_total')
    list_filter = ('producto', 'fecha_venta')
    search_fields = ('cliente__nombre', 'producto__nombre')

    def get_total(self, obj):
        return obj.total

    get_total.short_description = 'Total'
    get_total.admin_order_field = 'total'

@admin.register(MovimientoCliente)
class MovimientoClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_movimiento', 'fecha')
    search_fields = ('cliente__nombre', 'tipo_movimiento')
    list_filter = ('tipo_movimiento', 'fecha')
    readonly_fields = ('cliente', 'tipo_movimiento', 'descripcion', 'fecha')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_base', 'cantidad_disponible', 'es_reservable')
    search_fields = ('nombre',)
    list_filter = ('categoria', 'es_reservable')

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email', 'telefono', 'es_externo')
    search_fields = ('nombre', 'contacto', 'email')
    list_filter = ('es_externo',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cliente', 'fecha_reserva', 'cantidad', 'creado_en')
    search_fields = ('cliente__nombre', 'producto__nombre')
    list_filter = ('fecha_reserva',)

@admin.register(PrecioDinamico)
class PrecioDinamicoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'nombre_regla', 'precio', 'prioridad', 'fecha_inicio', 'fecha_fin')
    search_fields = ('producto__nombre', 'nombre_regla')
    list_filter = ('prioridad', 'fecha_inicio', 'fecha_fin', 'dia_semana', 'mes')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('venta', 'fecha_pago', 'monto', 'metodo_pago')
    search_fields = ('venta__id', 'venta__cliente__nombre')
    list_filter = ('metodo_pago', 'fecha_pago')
