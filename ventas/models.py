from django.db import models
from django.utils import timezone
from django.db.models import Q

# Proveedores
class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    contacto = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    es_externo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# Categoría de Producto
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    cantidad_disponible = models.PositiveIntegerField(default=0)
    es_reservable = models.BooleanField(default=False)
    duracion_reserva = models.DurationField(null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre

    def obtener_precio_actual(self, fecha_reserva=None):
        if not fecha_reserva:
            fecha_reserva = timezone.now()
        else:
            if isinstance(fecha_reserva, str):
                fecha_reserva = timezone.datetime.fromisoformat(fecha_reserva)
        fecha_reserva = timezone.make_aware(fecha_reserva, timezone.get_current_timezone())

        reglas = PrecioDinamico.objects.filter(producto=self).filter(
            Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=fecha_reserva.date()),
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=fecha_reserva.date()),
            Q(hora_inicio__isnull=True) | Q(hora_inicio__lte=fecha_reserva.time()),
            Q(hora_fin__isnull=True) | Q(hora_fin__gte=fecha_reserva.time()),
            Q(dia_semana__isnull=True) | Q(dia_semana=fecha_reserva.isoweekday()),
            Q(mes__isnull=True) | Q(mes=fecha_reserva.month)
        ).order_by('-prioridad')

        if reglas.exists():
            return reglas.first().precio
        return self.precio_base

# Precio Dinámico
class PrecioDinamico(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} - {self.precio}"

# Cliente
class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.nombre
    
class MovimientoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.cliente.nombre} - {self.fecha}"

# VentaReserva
class VentaReserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ReservaProducto')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_reserva = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('pagado', 'Pagado'),
            ('parcial', 'Parcialmente Pagado'),
            ('cancelado', 'Cancelado'),
        ],
        default='pendiente'
    )

    def __str__(self):
        return f"Venta/Reserva #{self.id} de {self.cliente}"

    def calcular_total(self):
        total = 0
        for reserva_producto in self.reservaprodutos.all():
            precio = reserva_producto.producto.obtener_precio_actual(self.fecha_reserva)
            total += precio * reserva_producto.cantidad
        self.total = total
        self.save()

    def actualizar_pago(self):
        total_pagado = self.pagos.aggregate(models.Sum('monto'))['monto__sum'] or 0
        self.pagado = total_pagado
        self.saldo_pendiente = self.total - total_pagado
        if self.saldo_pendiente <= 0:
            self.estado = 'pagado'
            self.saldo_pendiente = 0
        elif total_pagado > 0:
            self.estado = 'parcial'
        else:
            self.estado = 'pendiente'
        self.save(update_fields=['pagado', 'saldo_pendiente', 'estado'])

# ReservaProducto
class ReservaProducto(models.Model):
    venta_reserva = models.ForeignKey(VentaReserva, on_delete=models.CASCADE, related_name='reservaprodutos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_agendamiento = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Venta/Reserva #{self.venta_reserva.id}"

# Pago
class Pago(models.Model):
    venta_reserva = models.ForeignKey(VentaReserva, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(
        max_length=50,
        choices=[
            ('efectivo', 'Efectivo'),
            ('tarjeta', 'Tarjeta de Crédito/Débito'),
            ('transferencia', 'Transferencia Bancaria'),
            ('paypal', 'PayPal'),
        ]
    )

    def __str__(self):
        return f"Pago de {self.monto} para {self.venta_reserva}"
