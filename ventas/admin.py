from django.contrib import admin
from .models import VentaReserva, ReservaProducto, Cliente, Producto, Pago

# Admin para ReservaProducto en línea dentro de VentaReserva
class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

# Admin para VentaReserva
@admin.register(VentaReserva)
class VentaReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    inlines = [ReservaProductoInline]
    search_fields = ('cliente__nombre',)
    list_filter = ('estado', 'fecha_reserva')
    readonly_fields = ('total', 'pagado', 'saldo_pendiente')

# Admin para Pago
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta_reserva', 'fecha_pago', 'monto')
    search_fields = ('venta_reserva__cliente__nombre',)
