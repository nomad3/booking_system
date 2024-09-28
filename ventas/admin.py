from django.contrib import admin
from .models import VentaReserva, ReservaProducto, Pago, Cliente, Producto, Proveedor, CategoriaProducto

# Inline para agregar productos en la misma vista de la reserva
class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

# Inline para agregar pagos en la misma vista de la reserva
class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

# Test Auto Deploy
# Administración de VentaReserva
@admin.register(VentaReserva)
class VentaReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline, PagoInline]
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    search_fields = ['cliente__nombre']
    list_filter = ['estado', 'fecha_reserva']
    readonly_fields = ('total', 'pagado', 'saldo_pendiente')

    def save_model(self, request, obj, form, change):
        # Guarda la instancia de VentaReserva primero
        if not change:
            obj.save()

        # Ahora que la instancia tiene un primary key, calcular el total y actualizar pagos
        obj.calcular_total()
        obj.actualizar_pago()

        super().save_model(request, obj, form, change)

# Registro de los demás modelos
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'cantidad_disponible', 'es_reservable', 'categoria')
    search_fields = ['nombre']
    list_filter = ['categoria']

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ['nombre']

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'telefono', 'email', 'es_externo')
    search_fields = ['nombre', 'contacto']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')
    search_fields = ['nombre', 'email']
