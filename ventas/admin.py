from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, ReservaServicio, Pago, Cliente, Servicio


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
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    search_fields = ['cliente__nombre']
    list_filter = ['estado']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # When updating an existing object
            return ['total', 'pagado', 'saldo_pendiente', 'estado']
        return []


class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email')


class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'categoria', 'cantidad_disponible')


class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'duracion')


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')


class PagoAdmin(admin.ModelAdmin):
    list_display = ('venta_reserva', 'monto', 'metodo_pago')


admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CategoriaProducto, CategoriaProductoAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(VentaReserva, VentaReservaAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Pago, PagoAdmin)
