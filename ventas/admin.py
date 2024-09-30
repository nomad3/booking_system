from django.contrib import admin
from django import forms
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente, CategoriaServicio, Servicio, ReservaServicio

# Formulario personalizado para elegir los slots de horas según el servicio
class ReservaServicioInlineForm(forms.ModelForm):
    class Meta:
        model = ReservaServicio
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ReservaServicioInlineForm, self).__init__(*args, **kwargs)

        # Obtener el servicio desde la instancia si existe
        servicio = self.instance.servicio if self.instance else None

        # Definir las opciones de hora según el tipo de servicio
        if servicio:
            if servicio.categoria.nombre == 'Cabañas':
                self.fields['fecha_agendamiento'].widget = forms.Select(choices=[
                    ('16:00', '16:00'),
                ])
            elif servicio.categoria.nombre == 'Tinas':
                self.fields['fecha_agendamiento'].widget = forms.Select(choices=[
                    ('14:00', '14:00'),
                    ('14:30', '14:30'),
                    ('17:00', '17:00'),
                    ('19:00', '19:00'),
                    ('19:30', '19:30'),
                    ('21:30', '21:30'),
                    ('22:00', '22:00'),
                ])
            elif servicio.categoria.nombre == 'Masajes':
                self.fields['fecha_agendamiento'].widget = forms.Select(choices=[
                    ('13:00', '13:00'),
                    ('14:15', '14:15'),
                    ('15:30', '15:30'),
                    ('16:45', '16:45'),
                    ('18:00', '18:00'),
                    ('19:15', '19:15'),
                    ('20:30', '20:30'),
                ])
class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1


class ReservaServicioInline(admin.TabularInline):
    model = ReservaServicio
    form = ReservaServicioInlineForm  # Usar el formulario personalizado
    extra = 1

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1


class VentaReservaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado')
    readonly_fields = ('total','pagado','saldo_pendiente')
    inlines = [ReservaProductoInline, ReservaServicioInline, PagoInline]
    list_filter = ('cliente', 'servicios', 'fecha_reserva','estado')
    search_fields = ('cliente__nombre', 'cliente__email','cliente__telefono')

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email')


class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'cantidad_disponible', 'categoria', 'proveedor')


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')


class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'duracion', 'categoria', 'proveedor')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('venta_reserva', 'monto', 'metodo_pago', 'fecha_pago')

admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CategoriaProducto, CategoriaProductoAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(VentaReserva, VentaReservaAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(CategoriaServicio)
