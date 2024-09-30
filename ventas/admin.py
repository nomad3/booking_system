from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, Servicio, VentaReserva, ReservaProducto, ReservaServicio, Pago, Cliente, MovimientoCliente


class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1


class ReservaServicioInline(admin.TabularInline):
    model = ReservaServicio
    extra = 1


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1


class VentaReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline, ReservaServicioInline, PagoInline]
    list_display = ('id', 'cliente', 'total', 'pagado', 'saldo_pendiente', 'estado')
    search_fields = ['cliente__nombre']


class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email')


class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'categoria', 'cantidad_disponible', 'proveedor')


class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion', 'precio_base')


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')


class MovimientoClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_movimiento', 'descripcion', 'fecha')


admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CategoriaProducto, CategoriaProductoAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(VentaReserva, VentaReservaAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(MovimientoCliente, MovimientoClienteAdmin)
