from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente

class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

class VentaReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline, PagoInline]
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')  # Removed 'fecha_creacion'
    search_fields = ['cliente__nombre']

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email')

class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'categoria', 'cantidad_disponible', 'es_reservable')

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')

admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CategoriaProducto, CategoriaProductoAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(VentaReserva, VentaReservaAdmin)
admin.site.register(Cliente, ClienteAdmin)
