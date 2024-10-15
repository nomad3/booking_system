from django.contrib import admin
from django import forms
from django.forms import DateTimeInput
from datetime import datetime
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.forms import DateInput, TimeInput, Select
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente, CategoriaServicio, Servicio, ReservaServicio, MovimientoCliente

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

# Método para registrar movimientos en el sistema
def registrar_movimiento(cliente, tipo_movimiento, descripcion, usuario):
    MovimientoCliente.objects.create(
        cliente=cliente,
        tipo_movimiento=tipo_movimiento,
        descripcion=descripcion,
        usuario=usuario
    )

class VentaReservaAdmin(admin.ModelAdmin):
    autocomplete_fields = ['cliente']
    list_display = (
        'id', 'cliente', 'fecha_reserva', 'estado', 
        'mostrar_categoria_servicios', 'mostrar_nombre_servicios', 
        'mostrar_cantidad_servicios', 'mostrar_total_servicios', 
        'mostrar_categoria_productos', 'mostrar_nombre_productos', 
        'mostrar_cantidad_productos', 'mostrar_total_productos', 
        'total', 'pagado', 'saldo_pendiente'
    )
    readonly_fields = ('total', 'pagado', 'saldo_pendiente')
    inlines = [ReservaProductoInline, ReservaServicioInline, PagoInline]
    list_filter = ('servicios', 'fecha_reserva', 'estado')
    search_fields = ('cliente__nombre', 'cliente__email', 'cliente__telefono')

    def save_model(self, request, obj, form, change):
        if change:
            tipo = "Actualización de Venta/Reserva"
            descripcion = f"Se ha actualizado la venta/reserva con ID {obj.id} para el cliente {obj.cliente.nombre}."
        else:
            tipo = "Creación de Venta/Reserva"
            descripcion = f"Se ha creado una nueva venta/reserva con ID {obj.id} para el cliente {obj.cliente.nombre}."
        super().save_model(request, obj, form, change)
        registrar_movimiento(obj.cliente, tipo, descripcion, request.user)

    def delete_model(self, request, obj):
        descripcion = f"Se ha eliminado la venta/reserva con ID {obj.id} del cliente {obj.cliente.nombre}."
        registrar_movimiento(obj.cliente, "Eliminación de Venta/Reserva", descripcion, request.user)
        super().delete_model(request, obj)

    # Mostrar categorías de servicios
    def mostrar_categoria_servicios(self, obj):
        return ", ".join([servicio.categoria.nombre for servicio in obj.servicios.all() if servicio.categoria])
    mostrar_categoria_servicios.short_description = 'Categoría de Servicios'

    # Mostrar nombres de servicios
    def mostrar_nombre_servicios(self, obj):
        return ", ".join([servicio.nombre for servicio in obj.servicios.all()])
    mostrar_nombre_servicios.short_description = 'Servicios'

    # Mostrar cantidad de servicios
    def mostrar_cantidad_servicios(self, obj):
        return ", ".join([str(reserva_servicio.cantidad_personas) for reserva_servicio in obj.reservaservicios.all()])
    mostrar_cantidad_servicios.short_description = 'Cantidad de Servicios'

    # Calcular total de servicios
    def mostrar_total_servicios(self, obj):
        total = sum([reserva_servicio.servicio.precio_base * reserva_servicio.cantidad_personas for reserva_servicio in obj.reservaservicios.all()])
        return f"{total} CLP"
    mostrar_total_servicios.short_description = 'Total de Servicios'

    # Mostrar categorías de productos
    def mostrar_categoria_productos(self, obj):
        return ", ".join([producto.categoria.nombre for producto in obj.productos.all() if producto.categoria])
    mostrar_categoria_productos.short_description = 'Categoría de Productos'

    # Mostrar nombres de productos
    def mostrar_nombre_productos(self, obj):
        return ", ".join([producto.nombre for producto in obj.productos.all()])
    mostrar_nombre_productos.short_description = 'Productos'

    # Mostrar cantidad de productos
    def mostrar_cantidad_productos(self, obj):
        return ", ".join([str(reserva_producto.cantidad) for reserva_producto in obj.reservaproductos.all()])
    mostrar_cantidad_productos.short_description = 'Cantidad de Productos'

    # Calcular total de productos
    def mostrar_total_productos(self, obj):
        total = sum([reserva_producto.producto.precio_base * reserva_producto.cantidad for reserva_producto in obj.reservaproductos.all()])
        return f"{total} CLP"
    mostrar_total_productos.short_description = 'Total de Productos'


class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email')

class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'cantidad_disponible', 'categoria', 'proveedor')

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')
    search_fields = ['nombre', 'telefono', 'email']

class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'duracion', 'categoria', 'proveedor')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('venta_reserva', 'monto', 'metodo_pago', 'fecha_pago')

    def save_model(self, request, obj, form, change):
        if change:
            tipo = "Actualización de Pago"
            descripcion = f"Se ha actualizado el pago de {obj.monto} para la venta/reserva #{obj.venta_reserva.id}."
        else:
            tipo = "Registro de Pago"
            descripcion = f"Se ha registrado un nuevo pago de {obj.monto} para la venta/reserva #{obj.venta_reserva.id}."
        super().save_model(request, obj, form, change)
        registrar_movimiento(obj.venta_reserva.cliente, tipo, descripcion, request.user)

    def delete_model(self, request, obj):
        descripcion = f"Se ha eliminado el pago de {obj.monto} de la venta/reserva #{obj.venta_reserva.id}."
        registrar_movimiento(obj.venta_reserva.cliente, "Eliminación de Pago", descripcion, request.user)
        super().delete_model(request, obj)

admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CategoriaProducto, CategoriaProductoAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(VentaReserva, VentaReservaAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(CategoriaServicio)
