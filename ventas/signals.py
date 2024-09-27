from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Venta, Cliente, MovimientoCliente, Pago, Reserva

# Señales para Venta
@receiver(post_save, sender=Venta)
def registrar_movimiento_venta(sender, instance, created, **kwargs):
    if created:
        tipo = 'Creación de Venta'
        descripcion = f"Se ha creado una nueva venta con ID {instance.id} para el cliente {instance.cliente.nombre}."
    else:
        tipo = 'Actualización de Venta'
        descripcion = f"Se ha actualizado la venta con ID {instance.id} para el cliente {instance.cliente.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

@receiver(post_delete, sender=Venta)
def registrar_movimiento_eliminacion_venta(sender, instance, **kwargs):
    tipo = 'Eliminación de Venta'
    descripcion = f"Se ha eliminado la venta con ID {instance.id} del cliente {instance.cliente.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

# Señales para Cliente
@receiver(post_save, sender=Cliente)
def registrar_movimiento_cliente(sender, instance, created, **kwargs):
    if created:
        tipo = 'Creación de Cliente'
        descripcion = f"Se ha creado un nuevo cliente: {instance.nombre}."
    else:
        tipo = 'Actualización de Cliente'
        descripcion = f"Se ha actualizado la información del cliente: {instance.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

@receiver(post_delete, sender=Cliente)
def registrar_movimiento_eliminacion_cliente(sender, instance, **kwargs):
    tipo = 'Eliminación de Cliente'
    descripcion = f"Se ha eliminado el cliente: {instance.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

# Señales para Pago
@receiver(post_save, sender=Pago)
def registrar_movimiento_pago(sender, instance, created, **kwargs):
    if created:
        tipo = 'Pago Realizado'
        descripcion = f"Se ha registrado un pago de {instance.monto} para la venta #{instance.venta.id} mediante {instance.metodo_pago}."
        
        MovimientoCliente.objects.create(
            cliente=instance.venta.cliente,
            tipo_movimiento=tipo,
            descripcion=descripcion
        )

# Señales para Reserva
@receiver(post_save, sender=Reserva)
def registrar_movimiento_reserva(sender, instance, created, **kwargs):
    if created:
        tipo = 'Creación de Reserva'
        descripcion = f"Se ha creado una reserva para el producto {instance.producto.nombre} por el cliente {instance.cliente.nombre} desde {instance.fecha_reserva}."
    else:
        tipo = 'Actualización de Reserva'
        descripcion = f"Se ha actualizado la reserva {instance.id} para el producto {instance.producto.nombre} por el cliente {instance.cliente.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

@receiver(post_delete, sender=Reserva)
def registrar_movimiento_eliminacion_reserva(sender, instance, **kwargs):
    tipo = 'Eliminación de Reserva'
    descripcion = f"Se ha eliminado la reserva para el producto {instance.producto.nombre} por el cliente {instance.cliente.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )
