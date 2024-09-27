from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q 
from django.core.exceptions import ValidationError  

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
        else:
            # Asegurarse de que fecha_reserva es un objeto datetime
            if isinstance(fecha_reserva, str):
                fecha_reserva = timezone.datetime.fromisoformat(fecha_reserva)

        # Convertir fecha_reserva a zona horaria activa si es naive
        if timezone.is_naive(fecha_reserva):
            fecha_reserva = timezone.make_aware(fecha_reserva, timezone.get_current_timezone())

        # Filtrar reglas que aplican al producto y al rango de fechas y otros criterios
        reglas = PrecioDinamico.objects.filter(producto=self).filter(
            Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=fecha_reserva),
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=fecha_reserva),
            Q(hora_inicio__isnull=True) | Q(hora_inicio__lte=fecha_reserva.time()),
            Q(hora_fin__isnull=True) | Q(hora_fin__gte=fecha_reserva.time()),
            Q(dia_semana__isnull=True) | Q(dia_semana=fecha_reserva.isoweekday()),
            Q(mes__isnull=True) | Q(mes=fecha_reserva.month)
        ).order_by('-prioridad')

        if reglas.exists():
            # Tomar la regla con mayor prioridad
            return reglas.first().precio
        return self.precio_base

class PrecioDinamico(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios_dinamicos')
    nombre_regla = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    prioridad = models.PositiveIntegerField(default=0)  # Mayor número, mayor prioridad
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
        return f"{self.producto.nombre} - {self.precio} ({self.nombre_regla})"

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
            raise ValidationError('Cantidad no disponible')
        
        super(Reserva, self).save(*args, **kwargs)

        if self.producto.es_reservable:
            # Comentamos temporalmente la conexión con Google Calendar
            # from .utils import crear_evento_calendar
            # crear_evento_calendar(self)
            pass  # Puedes reemplazar con cualquier otra lógica si es necesario

        # Actualizar la cantidad disponible
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
