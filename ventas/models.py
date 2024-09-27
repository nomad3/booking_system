# ventas/models.py

from django.db import models, transaction
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.cache import cache
from datetime import timedelta

class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    correo_electronico = models.EmailField(unique=True, db_index=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.correo_electronico})"

    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
        ]

class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    contacto = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    es_externo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class CategoriaProducto(models.Model):
    TIPO_DURACION_CHOICES = [
        ('dia', 'Día Completo'),
        ('hora', 'Hora'),
        ('minuto', 'Minuto'),
    ]
    nombre = models.CharField(max_length=100)
    tipo_duracion = models.CharField(
        max_length=10,
        choices=TIPO_DURACION_CHOICES,
        default='dia'  # Valor por defecto para evitar errores en migraciones
    )

    def __str__(self):
        return self.nombre

    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
        ]

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    cantidad_disponible = models.PositiveIntegerField(default=0)
    es_reservable = models.BooleanField(default=False)
    
    # Campos para duración de reserva
    duracion_reserva_valor = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text='Cantidad de tiempo para la reserva.'
    )
    DURACION_UNIDAD_CHOICES = [
        ('minuto', 'Minuto'),
        ('hora', 'Hora'),
        ('dia', 'Día'),
    ]
    duracion_reserva_unidad = models.CharField(
        max_length=10,
        choices=DURACION_UNIDAD_CHOICES,
        null=True,
        blank=True,
        help_text='Unidad de tiempo para la reserva.'
    )
    duracion_reserva = models.DurationField(null=True, blank=True, editable=False)

    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre

    def obtener_precio_actual(self, fecha_reserva=None):
        if not fecha_reserva:
            fecha_reserva = timezone.now()
        else:
            if isinstance(fecha_reserva, str):
                fecha_reserva = timezone.datetime.fromisoformat(fecha_reserva)

        if timezone.is_naive(fecha_reserva):
            fecha_reserva = timezone.make_aware(fecha_reserva, timezone.get_current_timezone())

        cache_key = f"precio_{self.id}_{fecha_reserva.strftime('%Y%m%d%H%M')}"
        precio = cache.get(cache_key)

        if precio is None:
            # Obtener reglas aplicables
            reglas = self.precios_dinamicos.filter(
                Q(tipo_regla='fecha', valor_regla=fecha_reserva.date()) |
                Q(tipo_regla='hora', valor_regla=fecha_reserva.time().strftime('%H:%M')) |
                Q(tipo_regla='dia_semana', valor_regla=fecha_reserva.isoweekday()) |
                Q(tipo_regla='mes', valor_regla=fecha_reserva.month)
            ).filter(
                Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=fecha_reserva),
                Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=fecha_reserva)
            ).order_by('-prioridad')

            if reglas.exists():
                precio = reglas.first().precio
            else:
                precio = self.precio_base

            cache.set(cache_key, precio, timeout=60*60)  # Cachear por 1 hora

        return precio

    def clean(self):
        super().clean()
        if self.es_reservable:
            if not self.duracion_reserva_valor or not self.duracion_reserva_unidad:
                raise ValidationError('Debe especificar tanto el valor como la unidad de duración de la reserva si el producto es reservable.')
        else:
            self.duracion_reserva_valor = None
            self.duracion_reserva_unidad = None
            self.duracion_reserva = None

    def save(self, *args, **kwargs):
        self.clean()
        if self.es_reservable and self.duracion_reserva_valor and self.duracion_reserva_unidad:
            if self.duracion_reserva_unidad == 'minuto':
                self.duracion_reserva = timedelta(minutes=self.duracion_reserva_valor)
            elif self.duracion_reserva_unidad == 'hora':
                self.duracion_reserva = timedelta(hours=self.duracion_reserva_valor)
            elif self.duracion_reserva_unidad == 'dia':
                self.duracion_reserva = timedelta(days=self.duracion_reserva_valor)
        else:
            self.duracion_reserva = None

        super(Producto, self).save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['precio_base']),
        ]

class PrecioDinamico(models.Model):
    TIPO_REGLA_CHOICES = [
        ('fecha', 'Fecha'),
        ('hora', 'Hora'),
        ('dia_semana', 'Día de la Semana'),
        ('mes', 'Mes'),
    ]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios_dinamicos')
    nombre_regla = models.CharField(max_length=255, default='Regla Predeterminada')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    prioridad = models.PositiveIntegerField(default=0)
    tipo_regla = models.CharField(
        max_length=20,
        choices=TIPO_REGLA_CHOICES,
        default='fecha'  # Valor por defecto para evitar errores en migraciones
    )
    valor_regla = models.CharField(max_length=100)  # Ejemplo: '2023-12-25', '18:00', '1', '12'
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.precio} ({self.nombre_regla})"

    class Meta:
        ordering = ['-prioridad']
        indexes = [
            models.Index(fields=['tipo_regla', 'valor_regla']),
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['fecha_fin']),
        ]

class Reserva(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reservas')
    cantidad = models.PositiveIntegerField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva de {self.producto.nombre} por {self.cliente.nombre} desde {self.fecha_inicio} hasta {self.fecha_fin}"

    def clean(self):
        super().clean()
        # Validar que fecha_fin es posterior a fecha_inicio
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')

        # Obtener el tipo de duración de la reserva
        tipo_duracion = self.producto.categoria.tipo_duracion

        if tipo_duracion == 'dia':
            # Redondear fechas al inicio del día
            self.fecha_inicio = self.fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
            self.fecha_fin = self.fecha_fin.replace(hour=23, minute=59, second=59, microsecond=999999)

            overlapping_reservas = Reserva.objects.filter(
                producto=self.producto,
                fecha_inicio__date=self.fecha_inicio.date()
            ).exclude(id=self.id)
            if overlapping_reservas.exists():
                raise ValidationError('Ya existe una reserva para este producto en la fecha seleccionada.')

        elif tipo_duracion in ['hora', 'minuto']:
            overlapping_reservas = Reserva.objects.filter(
                producto=self.producto,
                fecha_inicio__lt=self.fecha_fin,
                fecha_fin__gt=self.fecha_inicio
            ).exclude(id=self.id)
            if overlapping_reservas.exists():
                raise ValidationError('Ya existe una reserva para este producto en el intervalo de tiempo seleccionado.')
        
        else:
            raise ValidationError('Tipo de duración de reserva no reconocido.')

    def save(self, *args, **kwargs):
        self.clean()
        with transaction.atomic():
            super(Reserva, self).save(*args, **kwargs)
            # Actualizar la cantidad disponible
            self.producto.cantidad_disponible -= self.cantidad
            self.producto.save()

    class Meta:
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['producto', 'fecha_inicio', 'fecha_fin']),
        ]

class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='ventas')
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

    def __str__(self):
        return f"Venta {self.id} - Cliente: {self.cliente.nombre}"

    def clean(self):
        super().clean()
        if self.pagado < 0:
            raise ValidationError('El monto pagado no puede ser negativo.')
        if self.pagado > self.total:
            raise ValidationError('El monto pagado no puede exceder el total de la venta.')

    def save(self, *args, **kwargs):
        self.clean()
        self.saldo_pendiente = self.total - self.pagado
        if self.saldo_pendiente <= 0:
            self.estado = 'pagado'
            self.saldo_pendiente = 0
        elif self.pagado > 0:
            self.estado = 'parcial'
        else:
            self.estado = 'pendiente'
        super(Venta, self).save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['fecha_venta']),
            models.Index(fields=['cliente', 'producto']),
        ]

class MovimientoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        indexes = [
            models.Index(fields=['fecha']),
        ]

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

    def clean(self):
        super().clean()
        if self.monto <= 0:
            raise ValidationError('El monto del pago debe ser positivo.')
        if self.venta.pagado + self.monto > self.venta.total:
            raise ValidationError('El monto pagado excede el total de la venta.')

    def save(self, *args, **kwargs):
        self.clean()
        with transaction.atomic():
            super(Pago, self).save(*args, **kwargs)
            self.venta.pagado += self.monto
            if self.venta.pagado > self.venta.total:
                raise ValidationError('El monto pagado excede el total de la venta.')
            self.venta.save()
    
    class Meta:
        indexes = [
            models.Index(fields=['venta', 'fecha_pago']),
        ]
