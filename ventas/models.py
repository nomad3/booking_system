from django.db import models
from django.utils import timezone

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

        # Business logic to handle dynamic prices, seasonal offers, etc.
        precios_dinamicos = PrecioDinamico.objects.filter(
            producto=self,
            fecha_inicio__lte=fecha_reserva,
            fecha_fin__gte=fecha_reserva
        )

        if precios_dinamicos.exists():
            return precios_dinamicos.first().precio

        return self.precio_base


class PrecioDinamico(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} - {self.precio}"


class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.nombre


class VentaReserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ReservaProducto')
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
            ('cancelado', 'Cancelado')
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

    def agregar_producto(self, producto, cantidad):
        reserva_producto = ReservaProducto.objects.create(
            venta_reserva=self,
            producto=producto,
            cantidad=cantidad
        )
        self.calcular_total()
        self.actualizar_pago()


class ReservaProducto(models.Model):
    venta_reserva = models.ForeignKey('VentaReserva', on_delete=models.CASCADE, related_name='reservaprodutos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_agendamiento = models.DateTimeField(null=True, blank=True)  # Only relevant for reservable products

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Venta/Reserva #{self.venta_reserva.id}"

    def clean(self):
        # Validate that fecha_agendamiento is only provided for reservable products
        if self.producto and not self.producto.es_reservable and self.fecha_agendamiento:
            raise ValidationError("Fecha de agendamiento no es válida para productos no reservables.")
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
        return f"Pago de {self.monto} para Venta/Reserva #{self.venta_reserva.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.venta_reserva.actualizar_pago()
