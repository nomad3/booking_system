from django.contrib import admin
from .models import VentaReserva, ReservaProducto, Pago, Cliente, Producto, Proveedor, CategoriaProducto

class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

@admin.register(VentaReserva)
class VentaReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline, PagoInline]
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    readonly_fields = ('total', 'pagado', 'saldo_pendiente')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.save()

        obj.calcular_total()
        obj.actualizar_pago()

        super().save_model(request, obj, form, change)

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
