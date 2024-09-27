from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import VentaReserva, Cliente, MovimientoCliente, Pago, ReservaProducto

# Señales para la creación de Venta/Reserva
@receiver(post_save, sender=VentaReserva)
def registrar_movimiento_venta_reserva(sender, instance, created, **kwargs):
    productos = ", ".join([f"{rp.cantidad}x {rp.producto.nombre}" for rp in instance.reservaprodutos.all()])
    if created:
        tipo = 'Creación de Venta/Reserva'
        descripcion = f"Se ha creado una venta/reserva para los productos ({productos}) por el cliente {instance.cliente.nombre}."
    else:
        tipo = 'Actualización de Venta/Reserva'
        descripcion = f"Se ha actualizado la venta/reserva {instance.id} para los productos ({productos}) por el cliente {instance.cliente.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

# Señales para Pago
@receiver(post_save, sender=Pago)
def registrar_movimiento_pago(sender, instance, created, **kwargs):
    if created:
        tipo = 'Pago Realizado'
        descripcion = f"Se ha registrado un pago de {instance.monto} para el cliente {instance.cliente.nombre} en la venta/reserva asociada."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )
