from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Venta, Cliente, MovimientoCliente, Pago, Reserva, ReservaProducto

# Señales para la creación de reservas, ventas y pagos
@receiver(post_save, sender=Reserva)
def registrar_movimiento_reserva(sender, instance, created, **kwargs):
    productos = ", ".join([f"{rp.cantidad}x {rp.producto.nombre}" for rp in instance.reservaprodutos.all()])
    if created:
        tipo = 'Creación de Reserva'
        descripcion = f"Se ha creado una reserva para los productos ({productos}) por el cliente {instance.cliente.nombre}."
    else:
        tipo = 'Actualización de Reserva'
        descripcion = f"Se ha actualizado la reserva {instance.id} para los productos ({productos}) por el cliente {instance.cliente.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

@receiver(post_save, sender=Pago)
def registrar_movimiento_pago(sender, instance, created, **kwargs):
    if created:
        tipo = 'Pago Realizado'
        descripcion = f"Se ha registrado un pago de {instance.monto} para el cliente {instance.cliente.nombre} en la reserva/venta asociada."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )
