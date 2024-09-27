from django.contrib import admin
from .models import Cliente, Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago

class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

class VentaReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline]
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    readonly_fields = ('total', 'pagado', 'saldo_pendiente')

class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'monto', 'metodo_pago', 'venta_reserva')

admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(CategoriaProducto)
admin.site.register(Producto)
admin.site.register(VentaReserva, VentaReservaAdmin)
admin.site.register(Pago, PagoAdmin)
