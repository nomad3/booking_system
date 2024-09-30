from django import forms
from django.contrib import admin
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, ReservaServicio, Pago, Cliente, Servicio

class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1
    fields = ['producto', 'cantidad']

class ReservaServicioInline(admin.TabularInline):
    model = ReservaServicio
    extra = 1
    fields = ['servicio', 'fecha_agendamiento']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        for form in formset.forms:
            if hasattr(form.instance, 'servicio') and form.instance.servicio:
                form.fields['fecha_agendamiento'].widget = forms.DateTimeInput(attrs={'type': 'datetime-local'})
        return formset

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

class VentaReservaAdmin(admin.ModelAdmin):
    inlines = [ReservaProductoInline, ReservaServicioInline, PagoInline]
    list_display = ('id', 'cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    search_fields = ['cliente__nombre']

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email')

class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'categoria', 'cantidad_disponible')

class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base')

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')

admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CategoriaProducto, CategoriaProductoAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(VentaReserva, VentaReservaAdmin)
admin.site.register(Cliente, ClienteAdmin)
