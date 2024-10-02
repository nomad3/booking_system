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

    # Campos separados para fecha y hora
    fecha = forms.DateField(widget=DateInput(attrs={'type': 'date'}), required=True, label='Fecha')
    hora = forms.ChoiceField(required=True, label='Hora')  # Inicialmente vacío

    def __init__(self, *args, **kwargs):
        super(ReservaServicioInlineForm, self).__init__(*args, **kwargs)

        # Inicializar el campo de hora vacío si no hay servicio seleccionado
        self.fields['hora'].choices = []  # Dejar vacío hasta que se seleccione un servicio

        # Obtener el servicio y asignar las horas según la categoría del servicio
        if self.instance and self.instance.pk:
            servicio = self.instance.servicio
        else:
            servicio = None

        if servicio and servicio.categoria:
            self.asignar_horarios(servicio.categoria.nombre)

    def asignar_horarios(self, categoria_nombre):
        """
        Asigna los slots de horarios según la categoría del servicio.
        """
        if categoria_nombre == 'Cabañas':
            self.fields['hora'].choices = [('16:00', '16:00')]
        elif categoria_nombre == 'Tinas':
            self.fields['hora'].choices = [
                ('14:00', '14:00'),
                ('14:30', '14:30'),
                ('17:00', '17:00'),
                ('19:00', '19:00'),
                ('19:30', '19:30'),
                ('21:30', '21:30'),
                ('22:00', '22:00'),
            ]
        elif categoria_nombre == 'Masajes':
            self.fields['hora'].choices = [
                ('13:00', '13:00'),
                ('14:15', '14:15'),
                ('15:30', '15:30'),
                ('16:45', '16:45'),
                ('18:00', '18:00'),
                ('19:15', '19:15'),
                ('20:30', '20:30'),
            ]

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if fecha and hora:
            # Combinar la fecha y la hora en un objeto datetime
            fecha_hora_str = f"{fecha} {hora}"
            fecha_agendamiento = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")

            # Hacer que la fecha y hora sea "aware" (con zona horaria)
            cleaned_data['fecha_agendamiento'] = make_aware(fecha_agendamiento)

        return cleaned_data

class ReservaServicioInline(admin.TabularInline):
    model = ReservaServicio
    form = ReservaServicioInlineForm  # Usar el formulario personalizado
    extra = 1

class ReservaProductoInline(admin.TabularInline):
    model = ReservaProducto
    extra = 1

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1


class VentaReservaAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en el listado
    list_display = ('id', 'cliente', 'fecha_reserva', 'estado', 'total', 'pagado', 'saldo_pendiente')

    # Campos que serán solo de lectura en la vista de detalles
    readonly_fields = ('total', 'pagado', 'saldo_pendiente')

    # Agregar las relaciones de productos, servicios y pagos como inlines
    inlines = [ReservaProductoInline, ReservaServicioInline, PagoInline]

    # Filtros por cliente, servicio, fecha de reserva y estado
    list_filter = ('cliente', 'servicios', 'fecha_reserva', 'estado')

    # Búsqueda por nombre, email y teléfono del cliente
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
