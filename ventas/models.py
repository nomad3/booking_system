from django.db import models
from django.utils import timezone

class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class MovimientoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_movimiento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.cliente.nombre}"

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
        if isinstance(fecha_reserva, str):
            fecha_reserva = timezone.datetime.fromisoformat(fecha_reserva)
        if timezone.is_naive(fecha_reserva):
            fecha_reserva = timezone.make_aware(fecha_reserva, timezone.get_current_timezone())
        reglas = PrecioDinamico.objects.filter(producto=self).filter(
            Q(fecha_inicio__lte=fecha_reserva) | Q(fecha_inicio__isnull=True),
            Q(fecha_fin__gte=fecha_reserva) | Q(fecha_fin__isnull=True),
            Q(hora_inicio__lte=fecha_reserva.time()) | Q(hora_inicio__isnull=True),
            Q(hora_fin__gte=fecha_reserva.time()) | Q(hora_fin__isnull=True),
            Q(dia_semana=fecha_reserva.isoweekday()) | Q(dia_semana__isnull=True),
            Q(mes=fecha_reserva.month) | Q(mes__isnull=True)
        ).order_by('-prioridad')
        if reglas.exists():
            return reglas.first().precio
        return self.precio_base

class PrecioDinamico(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios_dinamicos')
    nombre_regla = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    prioridad = models.PositiveIntegerField(default=0)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    dia_semana = models.PositiveSmallIntegerField(null=True, blank=True, choices=[
        (1, 'Lunes'),
        (2, 'Martes'),
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ])
    mes = models.PositiveSmallIntegerField(null=True, blank=True, choices=[
        (1, 'Enero'),
        (2, 'Febrero'),
        (3, 'Marzo'),
        (4, 'Abril'),
        (5, 'Mayo'),
        (6, 'Junio'),
        (7, 'Julio'),
        (8, 'Agosto'),
        (9, 'Septiembre'),
        (10, 'Octubre'),
        (11, 'Noviembre'),
        (12, 'Diciembre'),
    ])
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_regla} - {self.producto.nombre} - {self.precio}"

class Reserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
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
        ahora = self.fecha_reserva or timezone.now()
        for reserva_producto in self.reservaprodutos.all():
            if reserva_producto.producto.es_reservable:
                precio = reserva_producto.producto.obtener_precio_actual(self.fecha_reserva)
            else:
                precio = reserva_producto.producto.precio_base
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

class ReservaProducto(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='reservaprodutos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Reserva #{self.reserva.id}"

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
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
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pagos')
    fecha_pago = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, choices=[
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('webpay', 'WebPay'),
    ])

    def __str__(self):
        return f'Pago de {self.monto} para Reserva #{self.reserva.id}'

    def save(self, *args, **kwargs):
        super(Pago, self).save(*args, **kwargs)
        self.reserva.actualizar_pago()
