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

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        # Ensure formset.forms is not a cached_property issue
        if hasattr(formset, 'forms'):
            for form in formset.forms:
                if form.instance and hasattr(form.instance, 'producto') and form.instance.producto.es_reservable:
                    form.fields['fecha_agendamiento'].widget.attrs['style'] = 'display: inline;'
                else:
                    form.fields['fecha_agendamiento'].widget.attrs['style'] = 'display: none;'

        return formset

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
admin.site.register(Servicio)
