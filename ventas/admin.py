# ventas/admin.py

from django.contrib import admin
from .models import (
    Cliente,
    Venta,
    MovimientoCliente,
    Producto,
    CategoriaProducto,
    Proveedor,
    Reserva,
    PrecioDinamico,
    Pago
)
from .forms import ProductoForm

# Definir Inlines primero
class MovimientoClienteInline(admin.TabularInline):
    model = MovimientoCliente
    extra = 0
    readonly_fields = ('tipo_movimiento', 'descripcion', 'fecha')
    can_delete = False
    show_change_link = False

class ReservaInline(admin.TabularInline):
    model = Reserva
    extra = 0
    readonly_fields = ('fecha_inicio', 'fecha_fin', 'cliente', 'cantidad', 'creado_en')
    can_delete = False
    show_change_link = False

# Registrar el modelo Cliente con los inlines
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo_electronico', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'correo_electronico')
    list_filter = ('fecha_registro',)
    inlines = [MovimientoClienteInline, ReservaInline]

# Registrar el modelo Venta
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cliente', 'fecha_venta', 'cantidad', 'total', 'pagado', 'saldo_pendiente', 'estado')
    list_filter = ('producto', 'fecha_venta', 'estado')
    search_fields = ('cliente__nombre', 'producto__nombre')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('cliente', 'producto')
    
    # Opcional: Mostrar el total como un campo legible
    def get_total(self, obj):
        return obj.total
    get_total.short_description = 'Total'
    get_total.admin_order_field = 'total'

# Registrar el modelo MovimientoCliente directamente (opcional)
@admin.register(MovimientoCliente)
class MovimientoClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_movimiento', 'fecha')
    search_fields = ('cliente__nombre', 'tipo_movimiento')
    list_filter = ('tipo_movimiento', 'fecha')
    readonly_fields = ('cliente', 'tipo_movimiento', 'descripcion', 'fecha')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('cliente')

# Registrar el modelo Producto con el formulario personalizado
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoForm
    list_display = ('nombre', 'categoria', 'precio_base', 'cantidad_disponible', 'es_reservable', 'proveedor')
    list_filter = ('categoria', 'es_reservable')
    search_fields = ('nombre', 'categoria__nombre')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('categoria', 'proveedor')

# Registrar el modelo CategoriaProducto
@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_duracion')
    search_fields = ('nombre',)
    list_filter = ('tipo_duracion',)

# Registrar el modelo Proveedor
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email', 'telefono', 'es_externo')
    search_fields = ('nombre', 'contacto', 'email')
    list_filter = ('es_externo',)

# Registrar el modelo Reserva
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cliente', 'fecha_inicio', 'fecha_fin', 'cantidad', 'creado_en')
    list_filter = ('producto', 'fecha_inicio', 'fecha_fin')
    search_fields = ('cliente__nombre', 'producto__nombre')
    readonly_fields = ('producto', 'cliente', 'fecha_inicio', 'fecha_fin', 'cantidad', 'creado_en')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('cliente', 'producto')

# Registrar el modelo PrecioDinamico
@admin.register(PrecioDinamico)
class PrecioDinamicoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'nombre_regla', 'precio', 'prioridad', 'tipo_regla', 'valor_regla', 'fecha_inicio', 'fecha_fin')
    list_filter = ('tipo_regla', 'valor_regla', 'fecha_inicio', 'fecha_fin', 'prioridad')
    search_fields = ('producto__nombre', 'nombre_regla', 'tipo_regla', 'valor_regla')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('producto')

# Registrar el modelo Pago
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('venta', 'fecha_pago', 'monto', 'metodo_pago')
    list_filter = ('metodo_pago', 'fecha_pago')
    search_fields = ('venta__id', 'venta__cliente__nombre')
    readonly_fields = ('venta', 'fecha_pago', 'monto', 'metodo_pago')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('venta', 'venta__cliente')
