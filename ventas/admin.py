from django.contrib import admin
from django import forms
from django.forms import DateTimeInput
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils.safestring import mark_safe
from django.forms import DateInput, TimeInput, Select
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente, CategoriaServicio, Servicio, ReservaServicio

# Formulario personalizado para elegir los slots de horas según el servicio
class ReservaServicioInlineForm(forms.ModelForm):
    class Meta:
        model = ReservaServicio
        fields = ['servicio', 'cantidad_personas', 'fecha_agendamiento']

    def __init__(self, *args, **kwargs):
        super(ReservaServicioInlineForm, self).__init__(*args, **kwargs)
        # Usar el widget adecuado para seleccionar fecha y hora
        self.fields['fecha_agendamiento'].widget = DateTimeInput(attrs={'type': 'datetime-local'})

    def clean_fecha_agendamiento(self):
        fecha_agendamiento = self.cleaned_data.get('fecha_agendamiento')

        # Verificar que no se esté tratando como lista
        if isinstance(fecha_agendamiento, list):
            raise forms.ValidationError("Fecha y hora no pueden ser una lista. Ingrese un valor válido.")

        if fecha_agendamiento and isinstance(fecha_agendamiento, str):
            try:
                # Convertir la fecha ingresada por el usuario a datetime si es necesario
                fecha_agendamiento = datetime.strptime(fecha_agendamiento, '%Y-%m-%dT%H:%M')
                fecha_agendamiento = timezone.make_aware(fecha_agendamiento)  # Hacer la fecha "timezone-aware"
            except ValueError:
                raise forms.ValidationError("El formato de la fecha y hora no es válido.")

        return fecha_agendamiento
    
class ReservaServicioInline(admin.TabularInline):
    model = ReservaServicio
    form = ReservaServicioInlineForm
    extra = 1

class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1


class VentaReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_reserva', 'estado', 'total', 'pagado', 'saldo_pendiente')
    readonly_fields = ('total', 'pagado', 'saldo_pendiente')
    inlines = [ReservaProductoInline, ReservaServicioInline, PagoInline]
    list_filter = ('cliente', 'servicios', 'fecha_reserva', 'estado')
    search_fields = ('cliente__nombre', 'cliente__email', 'cliente__telefono')

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
