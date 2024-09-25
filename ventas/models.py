from django.db import models
from django.utils import timezone
from datetime import timedelta

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

    def obtener_precio_actual(self):
        ahora = timezone.now()
        precios_dinamicos = PrecioDinamico.objects.filter(
            producto=self,
            fecha_inicio__lte=ahora,
            fecha_fin__gte=ahora
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

class Reserva(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField()
    cliente = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva de {self.producto.nombre} por {self.cliente}"

    def save(self, *args, **kwargs):
        if self.producto.cantidad_disponible < self.cantidad:
            raise ValueError('Cantidad no disponible')
        super().save(*args, **kwargs)
        if self.producto.es_reservable:
            from .utils import crear_evento_calendar
            crear_evento_calendar(self)
        self.producto.cantidad_disponible -= self.cantidad
        self.producto.save()

class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cliente = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo_pago = models.CharField(
        max_length=50,
        choices=[
            ('efectivo', 'Efectivo'),
            ('tarjeta', 'Tarjeta de Crédito/Débito'),
            ('transferencia', 'Transferencia Bancaria'),
            ('paypal', 'PayPal'),
        ],
        null=True,
        blank=True
    )
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

    def save(self, *args, **kwargs):
        self.saldo_pendiente = self.total - self.pagado
        if self.saldo_pendiente <= 0:
            self.estado = 'pagado'
            self.saldo_pendiente = 0
        elif self.pagado > 0:
            self.estado = 'parcial'
        else:
            self.estado = 'pendiente'
        super(Venta, self).save(*args, **kwargs)

    def __str__(self):
        return f'Venta #{self.id} - {self.producto.nombre}'
    
class Pago(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='pagos')
    fecha_pago = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, choices=[
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('paypal', 'PayPal'),
        # Agrega más métodos de pago según tus necesidades
    ])

    def __str__(self):
        return f'Pago de {self.monto} para Venta #{self.venta.id}'

    def save(self, *args, **kwargs):
        super(Pago, self).save(*args, **kwargs)
        # Actualizar el monto pagado en la venta asociada
        self.venta.pagado += self.monto
        self.venta.save()
