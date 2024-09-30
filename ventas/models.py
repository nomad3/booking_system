from django.db import models
from django.utils import timezone


class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    contacto = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    es_externo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


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

        # Check for dynamic pricing rules
        reglas = PrecioDinamico.objects.filter(producto=self)

        # Apply dynamic pricing rules based on reservation time (if applicable)
        reglas = reglas.filter(
            models.Q(fecha_inicio__isnull=True) | models.Q(fecha_inicio__lte=fecha_reserva.date()),
            models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=fecha_reserva.date())
        ).order_by('-prioridad')

        if reglas.exists():
            return reglas.first().precio

        return self.precio_base


class PrecioDinamico(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} - {self.precio}"


class VentaReserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ReservaProducto')
    fecha_reserva = models.DateTimeField(null=True, blank=True)  # Fecha de la reserva para productos reservables
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


class ReservaProducto(models.Model):
    venta_reserva = models.ForeignKey('VentaReserva', on_delete=models.CASCADE, related_name='reservaprodutos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_agendamiento = models.DateTimeField(null=True, blank=True)  # Fecha para agendar productos reservables

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Venta/Reserva #{self.venta_reserva.id}"


class Pago(models.Model):
    venta_reserva = models.ForeignKey(VentaReserva, on_delete=models.CASCADE, related_name='pagos')
    fecha_pago = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, choices=[
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('paypal', 'PayPal'),
    ])

    def __str__(self):
        return f'Pago de {self.monto} para Venta/Reserva #{self.venta_reserva.id}'

    def save(self, *args, **kwargs):
        super(Pago, self).save(*args, **kwargs)
        # Update the paid amount in the associated VentaReserva
        self.venta_reserva.actualizar_pago()
