from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente

# Inline para agregar productos en la misma vista de la reserva
class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

# Inline para agregar pagos en la misma vista de la reserva
class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

# Administración de VentaReserva
@admin.register(VentaReserva)
class VentaReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline, PagoInline]
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    search_fields = ['cliente__nombre']
    list_filter = ['estado', 'fecha_reserva']
    readonly_fields = ('total', 'pagado', 'saldo_pendiente')

    def save_model(self, request, obj, form, change):
        obj.calcular_total()
        obj.actualizar_pago()
        super().save_model(request, obj, form, change)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'telefono', 'email', 'es_externo')

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'precio_base', 'categoria', 'cantidad_disponible', 'es_reservable')

@admin.register(ReservaProducto)
class ReservaProductoAdmin(admin.ModelAdmin):
    list_display = ('venta_reserva', 'producto', 'cantidad', 'fecha_agendamiento')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('venta_reserva', 'monto', 'fecha_pago', 'metodo_pago')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')
