
from datetime import timedelta
from django.db import models
from django.utils import timezone

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_disponible = models.PositiveIntegerField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre

    def reducir_inventario(self, cantidad):
        if self.cantidad_disponible >= cantidad:
            self.cantidad_disponible -= cantidad
            self.save()
        else:
            raise ValueError('No hay suficiente inventario disponible.')

class CategoriaServicio(models.Model):
    nombre = models.CharField(max_length=100)
    horarios = models.CharField(max_length=200, help_text="Ingresa los horarios disponibles separados por comas. Ejemplo: 14:00, 15:30, 17:00", blank=True)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.DurationField(default=timedelta(hours=2))
    categoria = models.ForeignKey(CategoriaServicio, on_delete=models.SET_NULL, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    pais = models.CharField(max_length=100, null=True, blank=True)  # Nuevo campo País
    ciudad = models.CharField(max_length=100, null=True, blank=True)  # Nuevo campo Ciudad

    def __str__(self):
        return self.nombre

class VentaReserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ReservaProducto')
    servicios = models.ManyToManyField(Servicio, through='ReservaServicio')
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
        # Sumar los productos
        for reserva_producto in self.reservaprodutos.all():
            total += reserva_producto.producto.precio_base * reserva_producto.cantidad
        
        # Sumar los servicios multiplicando por la cantidad de personas
        for reserva_servicio in self.reservaservicios.all():
            total += reserva_servicio.servicio.precio_base * reserva_servicio.cantidad_personas

        self.total = total
        self.saldo_pendiente = total - self.pagado
        self.save()

    def actualizar_saldo(self):
        self.saldo_pendiente = self.total - self.pagado
        if self.saldo_pendiente <= 0:
            self.estado = 'pagado'
        elif self.pagado > 0:
            self.estado = 'parcial'
        else:
            self.estado = 'pendiente'
        self.save()

    def registrar_pago(self, monto, metodo_pago):
        nuevo_pago = Pago.objects.create(
            venta_reserva=self,
            monto=monto,
            metodo_pago=metodo_pago
        )
        self.pagado += monto
        self.actualizar_saldo()
        return nuevo_pago

    def agregar_producto(self, producto, cantidad):
        self.productos.add(producto, through_defaults={'cantidad': cantidad})
        producto.reducir_inventario(cantidad)
        self.calcular_total()
        self.actualizar_saldo()

    def agregar_servicio(self, servicio, fecha_agendamiento, cantidad_personas=1):
        """
        Agrega un servicio a la reserva, especificando la fecha de agendamiento y la cantidad de personas.
        """
        self.servicios.add(servicio, through_defaults={
            'fecha_agendamiento': fecha_agendamiento,
            'cantidad_personas': cantidad_personas  # Registrar la cantidad de personas
        })
        self.calcular_total()
        self.actualizar_saldo()

class Pago(models.Model):
    METODOS_PAGO = [
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('webpay', 'WebPay'),
    ]

    venta_reserva = models.ForeignKey(VentaReserva, related_name='pagos', on_delete=models.CASCADE)
    fecha_pago = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=100, choices=METODOS_PAGO)

    def __str__(self):
        return f"Pago de {self.monto} para {self.venta_reserva}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.venta_reserva.pagado += self.monto
        self.venta_reserva.actualizar_saldo()

class MovimientoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_movimiento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Movimiento de {self.cliente} - {self.tipo_movimiento}"

class ReservaProducto(models.Model):
    venta_reserva = models.ForeignKey(VentaReserva, on_delete=models.CASCADE, related_name='reservaprodutos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Venta/Reserva #{self.venta_reserva.id}"

class ReservaServicio(models.Model):
    venta_reserva = models.ForeignKey(VentaReserva, on_delete=models.CASCADE, related_name='reservaservicios')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha_agendamiento = models.DateTimeField(default=timezone.now)
    cantidad_personas = models.PositiveIntegerField(default=1)  # Nuevo campo para la cantidad de personas

    def __str__(self):
        return f"{self.servicio.nombre} reservado para {self.fecha_agendamiento}"

    def calcular_precio(self):
        return self.servicio.precio_base * self.cantidad_personas  # Multiplicar el precio por la cantidad de personas