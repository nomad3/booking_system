from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import VentaReserva, ReservaProducto, Pago, Cliente, MovimientoCliente

# Registrar movimientos en VentaReserva
@receiver(post_save, sender=VentaReserva)
def registrar_movimiento_venta(sender, instance, created, **kwargs):
    if created:
        tipo = 'Creación de Venta/Reserva'
        descripcion = f"Se ha creado una nueva venta/reserva con ID {instance.id} para el cliente {instance.cliente.nombre}."
    else:
        tipo = 'Actualización de Venta/Reserva'
        descripcion = f"Se ha actualizado la venta/reserva con ID {instance.id} para el cliente {instance.cliente.nombre}."

    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

@receiver(post_delete, sender=VentaReserva)
def registrar_movimiento_eliminacion_venta(sender, instance, **kwargs):
    tipo = 'Eliminación de Venta/Reserva'
    descripcion = f"Se ha eliminado la venta/reserva con ID {instance.id} del cliente {instance.cliente.nombre}."

    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

# Registrar movimientos en Pago
@receiver(post_save, sender=Pago)
def registrar_movimiento_pago(sender, instance, created, **kwargs):
    if created:
        tipo = 'Pago Realizado'
        descripcion = f"Se ha registrado un pago de {instance.monto} para la venta/reserva #{instance.venta_reserva.id}."

        MovimientoCliente.objects.create(
            cliente=instance.venta_reserva.cliente,
            tipo_movimiento=tipo,
            descripcion=descripcion
        )
