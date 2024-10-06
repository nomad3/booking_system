from django.contrib import admin
from django import forms
from django.forms import DateTimeInput
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.forms import DateInput, TimeInput, Select
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente, CategoriaServicio, Servicio, ReservaServicio

# Personalización del título de la administración
admin.site.site_header = _("Sistema de Gestión de Ventas")
admin.site.site_title = _("Panel de Administración")
admin.site.index_title = _("Bienvenido al Panel de Control")

# Formulario personalizado para elegir los slots de horas según el servicio
class ReservaServicioInlineForm(forms.ModelForm):
    class Meta:
        model = ReservaServicio
        fields = ['servicio', 'fecha_agendamiento', 'cantidad_personas']

    def clean_fecha_agendamiento(self):
        """
        Convertir el campo `fecha_agendamiento` en un objeto datetime si es necesario.
        """
        fecha_agendamiento = self.cleaned_data.get('fecha_agendamiento')

        # Verificar si fecha_agendamiento es un string y convertirlo a datetime
        if isinstance(fecha_agendamiento, str):
            try:
                fecha_agendamiento = datetime.strptime(fecha_agendamiento, '%Y-%m-%d %H:%M')
                fecha_agendamiento = timezone.make_aware(fecha_agendamiento)  # Asegurarnos de que sea "aware"
            except ValueError:
                raise forms.ValidationError("El formato de la fecha de agendamiento no es válido. Debe ser YYYY-MM-DD HH:MM.")

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
