from django.contrib import admin
from django import forms
from datetime import datetime
from django.utils.timezone import make_aware
from django.forms import DateInput, TimeInput, Select
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente, CategoriaServicio, Servicio, ReservaServicio

# Formulario personalizado para elegir los slots de horas según el servicio
class ReservaServicioInlineForm(forms.ModelForm):
    class Meta:
        model = ReservaServicio
        fields = ['servicio', 'cantidad_personas']  # Excluimos 'fecha_agendamiento'

    # Campo separado para fecha y hora
    fecha = forms.DateField(widget=DateInput(attrs={'type': 'date'}), required=True, label='Fecha')
    hora = forms.ChoiceField(required=True, label='Hora', choices=[('', 'Seleccione un horario')])

    def __init__(self, *args, **kwargs):
        super(ReservaServicioInlineForm, self).__init__(*args, **kwargs)

        # Inicializamos el campo 'hora' con una opción de selección por defecto
        self.fields['hora'].choices = [('', 'Seleccione un horario')]

        # Si la instancia tiene un servicio asignado
        if self.instance.pk and getattr(self.instance, 'servicio', None):
            servicio = self.instance.servicio
            if servicio and servicio.categoria:
                self.cargar_horarios(servicio.categoria)
        # Si se selecciona un servicio desde el formulario
        elif 'servicio' in self.data:
            try:
                servicio_id = int(self.data.get('servicio'))
                servicio = Servicio.objects.get(id=servicio_id)
                self.cargar_horarios(servicio.categoria)
            except (ValueError, Servicio.DoesNotExist):
                pass

    def cargar_horarios(self, categoria):
        """
        Carga los horarios disponibles desde la categoría del servicio.
        """
        if categoria.horarios:  # Si la categoría tiene horarios definidos
            horarios = [(hora.strip(), hora.strip()) for hora in categoria.horarios.split(',')]
            self.fields['hora'].choices = horarios
        else:
            self.fields['hora'].choices = [('', 'No hay horarios disponibles')]

    def clean(self):
        """
        Combina la fecha y la hora en el campo `fecha_agendamiento`.
        """
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if fecha and hora:
            # Combinar la fecha y la hora en un solo campo
            fecha_hora_str = f"{fecha} {hora}"
            fecha_agendamiento = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")

            # Asegurarnos de que la fecha tenga información de zona horaria
            cleaned_data['fecha_agendamiento'] = make_aware(fecha_agendamiento)

        return cleaned_data
    
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
