from django.db import models
from .google_calendar import create_google_calendar_event

# Modelo Cliente
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

# Modelo de Habitaciones
class Habitacion(models.Model):
    nombre = models.CharField(max_length=100)
    capacidad = models.IntegerField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)

    def calcular_precio(self, fecha_reserva):
        return self.precio_base  # Lógica de precios dinámicos podría ir aquí

    def __str__(self):
        return self.nombre

# Modelo Masajes
class Masaje(models.Model):
    tipo = models.CharField(max_length=100)
    duracion = models.DurationField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)

    def calcular_precio(self, fecha_reserva):
        return self.precio_base  # Lógica de precios dinámicos podría ir aquí

# Modelo TinasCalientes
class TinaCaliente(models.Model):
    nombre = models.CharField(max_length=100)
    capacidad = models.IntegerField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)

    def calcular_precio(self, fecha_reserva):
        return self.precio_base  # Lógica de precios dinámicos podría ir aquí

# Modelo Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    stock = models.IntegerField()
    precio_fijo = models.DecimalField(max_digits=10, decimal_places=2)

# Modelo de Venta (Pedidos)
class Venta(models.Model):
    productos_vendidos = models.ManyToManyField(Producto)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    @property
    def precio_total(self):
        return self.cantidad * self.producto.precio

# Modelo Reserva
class Reserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    habitacion = models.ForeignKey(Habitacion, null=True, blank=True, on_delete=models.CASCADE)
    masaje = models.ForeignKey(Masaje, null=True, blank=True, on_delete=models.CASCADE)
    tina_caliente = models.ForeignKey(TinaCaliente, null=True, blank=True, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calcular_total(self):
        total = 0
        if self.habitacion:
            total += self.habitacion.calcular_precio(self.fecha_inicio)
        if self.masaje:
            total += self.masaje.calcular_precio(self.fecha_inicio)
        if self.tina_caliente:
            total += self.tina_caliente.calcular_precio(self.fecha_inicio)
        self.total = total
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        create_google_calendar_event(self)
