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
        # Lógica para precios dinámicos basada en fecha y hora
        return self.precio_base  # Puedes agregar aquí la lógica de precios dinámicos

class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.nombre

# Definir el modelo MovimientoCliente
class MovimientoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)  # Relación con cliente
    tipo_movimiento = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_movimiento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Movimiento del cliente {self.cliente.nombre}: {self.tipo_movimiento}"

class ReservaProducto(models.Model):
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE, related_name='reservaprodutos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Reserva #{self.reserva.id}"

class Reserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)  # Relación con cliente
    productos = models.ManyToManyField(Producto, through='ReservaProducto')
    fecha_reserva = models.DateTimeField()
    creado_en = models.DateTimeField(auto_now_add=True)
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
        return f"Reserva #{self.id} de {self.cliente}"

    def calcular_total(self):
        total = 0
        for reserva_producto in self.reservaprodutos.all():
            precio = reserva_producto.producto.obtener_precio_actual(self.fecha_reserva)
            total += precio * reserva_producto.cantidad
        self.total = total

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

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)  # Relación con cliente
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, null=True, blank=True, related_name="ventas")
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente}"

    def actualizar_pago(self):
        total_pagado = self.pagos.aggregate(models.Sum('monto'))['monto__sum'] or 0
        self.pagado = total_pagado
        self.saldo_pendiente = self.total - total_pagado
        self.save()

class Pago(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)  # Relación directa con cliente
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, choices=[
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('paypal', 'PayPal'),
    ])

    def __str__(self):
        return f'Pago de {self.monto} para Cliente {self.cliente.nombre}'

    def save(self, *args, **kwargs):
        super(Pago, self).save(*args, **kwargs)
        # Actualizar el monto pagado en la reserva y la venta asociada
        if self.reserva:
            self.reserva.actualizar_pago()
        if self.venta:
            self.venta.actualizar_pago()
