from django.contrib import admin
from django import forms
from django.forms import DateTimeInput
from datetime import date, datetime, timedelta  # Importa date, datetime, y timedelta
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
    list_per_page = 50  
    autocomplete_fields = ['cliente']
    list_display = (
        'id', 'cliente', 'fecha_reserva', 'estado', 
        'servicios_y_cantidades', 'productos_y_cantidades', 
        'total_servicios', 'total_productos', 
        'total', 'pagado', 'saldo_pendiente'
    )
    readonly_fields = ('total', 'pagado', 'saldo_pendiente')
    inlines = [ReservaProductoInline, ReservaServicioInline, PagoInline]
    list_filter = ()  # Quita el filtro por defecto
    search_fields = ('cliente__nombre', 'cliente__email', 'cliente__telefono')
    list_per_page = 20  # Paginación

    def changelist_view(self, request, extra_context=None):
        # Filtros personalizados
        qs = self.get_queryset(request)
        
        # Filtro por categoría de servicio
        categoria_servicio = request.GET.get('categoria_servicio')
        if categoria_servicio:
            qs = qs.filter(servicios__categoria__id=categoria_servicio)

        # Filtro por nombre de servicio
        servicio = request.GET.get('servicio')
        if servicio:
            qs = qs.filter(servicios__id=servicio)

        # Filtro por fecha de inicio y fin
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            qs = qs.filter(fecha_reserva__date__gte=fecha_inicio)
        else:
            fecha_inicio = date.today()  # Fecha por defecto
            qs = qs.filter(fecha_reserva__date=fecha_inicio)  #Filtra solo por la fecha de hoy

        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            qs = qs.filter(fecha_reserva__date__lte=fecha_fin)

        # Calcular el monto total en el rango de fechas
        total_en_rango = qs.aggregate(total=Sum('total'))['total'] or 0

        extra_context = extra_context or {}
        extra_context['total_en_rango'] = total_en_rango

        # Pasar todas las categorías y servicios al contexto, no solo las filtradas
        extra_context['categorias_servicio'] = CategoriaServicio.objects.all()  # <-- Corrección
        extra_context['servicios'] = Servicio.objects.all() # <-- Corrección


        # Pasar las fechas seleccionadas al contexto (o la fecha de hoy si no se seleccionaron)
        extra_context['fecha_inicio'] = fecha_inicio.strftime('%Y-%m-%d')
        extra_context['fecha_fin'] = fecha_fin.strftime('%Y-%m-%d') if fecha_fin else ''

        # Llamar a changelist_view del padre con el queryset filtrado
        return super().changelist_view(request, extra_context=extra_context)
 
    # Guardar cambios con registro de movimiento
    def save_model(self, request, obj, form, change):
        if change:
            tipo = "Actualización de Venta/Reserva"
            descripcion = f"Se ha actualizado la venta/reserva con ID {obj.id} para el cliente {obj.cliente.nombre}."
        else:
            tipo = "Creación de Venta/Reserva"
            descripcion = f"Se ha creado una nueva venta/reserva con ID {obj.id} para el cliente {obj.cliente.nombre}."
        super().save_model(request, obj, form, change)
        registrar_movimiento(obj.cliente, tipo, descripcion, request.user)

    # Eliminar con registro de movimiento
    def delete_model(self, request, obj):
        descripcion = f"Se ha eliminado la venta/reserva con ID {obj.id} del cliente {obj.cliente.nombre}."
        registrar_movimiento(obj.cliente, "Eliminación de Venta/Reserva", descripcion, request.user)
        super().delete_model(request, obj)

    # Mostrar servicios junto con cantidades en la misma fila
    def servicios_y_cantidades(self, obj):
        servicios_list = [
            f"{reserva_servicio.servicio.nombre} (x{reserva_servicio.cantidad_personas})" 
            for reserva_servicio in obj.reservaservicios.all()
        ]
        return ", ".join(servicios_list)
    servicios_y_cantidades.short_description = 'Servicios y Cantidades'

    # Mostrar productos junto con cantidades en la misma fila
    def productos_y_cantidades(self, obj):
        productos_list = [
            f"{reserva_producto.producto.nombre} (x{reserva_producto.cantidad})" 
            for reserva_producto in obj.reservaproductos.all()
        ]
        return ", ".join(productos_list)
    productos_y_cantidades.short_description = 'Productos y Cantidades'

    # Calcular total de servicios
    def total_servicios(self, obj):
        total = sum(
            reserva_servicio.servicio.precio_base * reserva_servicio.cantidad_personas 
            for reserva_servicio in obj.reservaservicios.all()
        )
        return f"{total} CLP"
    total_servicios.short_description = 'Total de Servicios'

    # Calcular total de productos
    def total_productos(self, obj):
        total = sum(
            reserva_producto.producto.precio_base * reserva_producto.cantidad 
            for reserva_producto in obj.reservaproductos.all()
        )
        return f"{total} CLP"
    total_productos.short_description = 'Total de Productos'

    # Optimización de consultas con prefetch_related
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related(
            'reservaproductos__producto',
            'reservaservicios__servicio',
        ).select_related('cliente')
        return queryset

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
