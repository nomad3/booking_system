from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente, CategoriaServicio, Servicio, ReservaServicio


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
    list_display = ('cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    inlines = [ReservaProductoInline, ReservaServicioInline, PagoInline]

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email')


class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'cantidad_disponible', 'categoria', 'proveedor')


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')


class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'duracion', 'categoria', 'proveedor')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('venta_reserva', 'monto', 'metodo_pago', 'fecha_pago')

admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CategoriaProducto, CategoriaProductoAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(VentaReserva, VentaReservaAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(CategoriaServicio)
