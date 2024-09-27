from django.contrib import admin
from .models import Cliente, Proveedor, CategoriaProducto, Producto, Reserva, ReservaProducto, Venta, Pago

class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

class ReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline]
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    readonly_fields = ('total', 'pagado', 'saldo_pendiente')

class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'total', 'pagado', 'saldo_pendiente')
    readonly_fields = ('total', 'pagado', 'saldo_pendiente')

class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'monto', 'metodo_pago', 'reserva', 'venta')

admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(CategoriaProducto)
admin.site.register(Producto)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(Venta, VentaAdmin)
admin.site.register(Pago, PagoAdmin)
