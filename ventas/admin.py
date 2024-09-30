from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente

class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        def formfield_callback(field, **form_kwargs):
            if field.name == 'fecha_agendamiento':
                form_kwargs['required'] = False
            return field.formfield(**form_kwargs)

        # Add a check if form.instance exists and has a valid product
        for form in formset.forms:
            if hasattr(form.instance, 'producto') and form.instance.producto:
                if form.instance.producto.es_reservable:
                    # Display date field for reservable products
                    form.fields['fecha_agendamiento'].required = True
                    form.fields['fecha_agendamiento'].widget = forms.DateTimeInput(attrs={'type': 'datetime-local'})
                else:
                    # Hide date field for non-reservable products
                    form.fields['fecha_agendamiento'].widget = forms.HiddenInput()

        return formset
class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

class VentaReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline, PagoInline]
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    search_fields = ['cliente__nombre']
    readonly_fields = ['total', 'pagado', 'saldo_pendiente']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # In edit mode, make these fields read-only
            return self.readonly_fields + ['cliente', 'fecha_reserva']
        return self.readonly_fields

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
