from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente


class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        for form in formset.forms:
            form.fields['fecha_agendamiento'].required = form.instance.producto.es_reservable if form.instance.producto else False
        return formset


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1


class VentaReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline, PagoInline]
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    search_fields = ['cliente__nombre']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj and obj.productos.filter(es_reservable=True).exists():
            fields.append('fecha_reserva')
        return fields


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
