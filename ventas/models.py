from django.db import models


class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    contacto = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_disponible = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre

    def obtener_precio_actual(self):
        return self.precio_base


class Servicio(models.Model):
    nombre = models.CharField(max_length=255)
    duracion = models.DurationField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

    def obtener_precio_actual(self):
        return self.precio_base


class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre


class VentaReserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ReservaProducto', blank=True)
    servicios = models.ManyToManyField(Servicio, through='ReservaServicio', blank=True)
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
        for reserva_producto in self.reservaproductos.all():
            total += reserva_producto.producto.obtener_precio_actual() * reserva_producto.cantidad
        for reserva_servicio in self.reservaservicios.all():
            total += reserva_servicio.servicio.obtener_precio_actual()
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
    venta_reserva = models.ForeignKey(VentaReserva, on_delete=models.CASCADE, related_name='reservaproductos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Venta/Reserva #{self.venta_reserva.id}"


class ReservaServicio(models.Model):
    venta_reserva = models.ForeignKey(VentaReserva, on_delete=models.CASCADE, related_name='reservaservicios')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha_agendamiento = models.DateTimeField()

    def __str__(self):
        return f"Servicio {self.servicio.nombre} agendado para {self.fecha_agendamiento} en Venta/Reserva #{self.venta_reserva.id}"


class Pago(models.Model):
    venta_reserva = models.ForeignKey(VentaReserva, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=255)

    def __str__(self):
        return f"Pago de {self.monto} para Venta/Reserva #{self.venta_reserva.id}"


class MovimientoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Movimiento para {self.cliente.nombre}: {self.tipo_movimiento}"
