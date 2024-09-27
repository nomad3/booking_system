from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, PrecioDinamico, Reserva, ReservaProducto, Pago, Cliente, MovimientoCliente, Venta

class PrecioDinamicoInline(admin.TabularInline):
    model = PrecioDinamico
    extra = 1

class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

class ProductoAdmin(admin.ModelAdmin):
    inlines = [PrecioDinamicoInline]
    list_display = ('nombre', 'precio_base', 'categoria', 'cantidad_disponible', 'es_reservable')
    list_filter = ('categoria', 'es_reservable', 'proveedor')
    search_fields = ('nombre', 'descripcion')

class ReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline, PagoInline]
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado', 'creado_en')
    list_filter = ('estado', 'fecha_reserva', 'creado_en')
    search_fields = ('cliente__nombre', 'id')
    readonly_fields = ('total', 'pagado', 'saldo_pendiente', 'estado', 'creado_en')

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email', 'telefono', 'es_externo')
    list_filter = ('es_externo',)
    search_fields = ('nombre', 'contacto', 'email', 'telefono')

class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')
    search_fields = ('nombre', 'email', 'telefono')

class MovimientoClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_movimiento', 'descripcion', 'fecha_movimiento')
    list_filter = ('fecha_movimiento',)
    search_fields = ('cliente__nombre', 'tipo_movimiento')

admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CategoriaProducto, CategoriaProductoAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(MovimientoCliente, MovimientoClienteAdmin)
admin.site.register(Venta)
admin.site.register(Pago)
