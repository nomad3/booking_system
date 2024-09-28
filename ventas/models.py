from django.db import models
from django.utils import timezone

# Modelo Cliente
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

# Modelo Proveedor
class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    contacto = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    es_externo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# Modelo CategoriaProducto
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Modelo Producto
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
            # Asegurarse de que fecha_reserva es un objeto datetime
            if isinstance(fecha_reserva, str):
                fecha_reserva = timezone.datetime.fromisoformat(fecha_reserva)

        # Convertir fecha_reserva a zona horaria activa
        fecha_reserva = timezone.make_aware(fecha_reserva, timezone.get_current_timezone())

        # Filtrar reglas que aplican al producto
        reglas = PrecioDinamico.objects.filter(producto=self)

        # Filtrar reglas que aplican en base a la fecha y hora
        reglas = reglas.filter(
            Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=fecha_reserva.date()),
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=fecha_reserva.date()),
            Q(hora_inicio__isnull=True) | Q(hora_inicio__lte=fecha_reserva.time()),
            Q(hora_fin__isnull=True) | Q(hora_fin__gte=fecha_reserva.time()),
            Q(dia_semana__isnull=True) | Q(dia_semana=fecha_reserva.isoweekday()),
            Q(mes__isnull=True) | Q(mes=fecha_reserva.month)
        ).order_by('-prioridad')  # Aquí estaba el error corregido

        if reglas.exists():
            # Tomar la regla con mayor prioridad
            return reglas.first().precio
        return self.precio_base
    
# Modelo VentaReserva (Unificación de Venta y Reserva)
class VentaReserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ReservaProducto')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_reserva = models.DateTimeField(null=True, blank=True)  # Fecha de la reserva general
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
        """Calcula el total de la reserva sumando el precio total de todos los productos reservados."""
        total = sum(reserva_producto.obtener_precio_total() for reserva_producto in self.reserva_productos.all())
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
# Modelo ReservaProducto (para manejar productos reservables)
class ReservaProducto(models.Model):
    venta_reserva = models.ForeignKey('VentaReserva', on_delete=models.CASCADE, related_name='reserva_productos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_agendamiento = models.DateTimeField(null=True, blank=True)  # Fecha para agendar productos reservables

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Venta/Reserva #{self.venta_reserva.id}"

    def obtener_precio_total(self):
        """Calcula el precio total de este producto en la reserva considerando la cantidad."""
        precio = self.producto.obtener_precio_actual(self.fecha_agendamiento)
        return precio * self.cantidad
# Modelo Pago
class Pago(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
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
        return f'Pago de {self.monto} para Cliente {self.cliente.nombre}'

    def save(self, *args, **kwargs):
        super(Pago, self).save(*args, **kwargs)
        self.venta_reserva.actualizar_pago()
