from django import forms
from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente

class ReservaProductoForm(forms.ModelForm):
    class Meta:
        model = ReservaProducto
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ensure that product is selected before accessing its attributes
        if self.instance and self.instance.producto:
            producto = self.instance.producto
            if not producto.es_reservable:
                self.fields['fecha_agendamiento'].widget = forms.HiddenInput()  # Hide field if product is not reservable
            else:
                self.fields['fecha_agendamiento'].required = True  # Require the field for reservable products
        else:
            # Hide the field by default if no product is selected yet
            self.fields['fecha_agendamiento'].widget = forms.HiddenInput()

class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1
    form = ReservaProductoForm

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

class VentaReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline, PagoInline]
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    search_fields = ['cliente__nombre']
    readonly_fields = ['total', 'pagado', 'saldo_pendiente', 'estado']

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
