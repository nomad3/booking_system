from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import VentaReserva, Cliente, ReservaProducto, ReservaServicio, Pago, MovimientoCliente


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


@receiver(post_save, sender=Pago)
def registrar_movimiento_pago(sender, instance, created, **kwargs):
    if created:
        tipo = 'Pago Realizado'
        descripcion = f"Se ha registrado un pago de {instance.monto} para la venta/reserva #{instance.venta_reserva.id} mediante {instance.metodo_pago}."

        MovimientoCliente.objects.create(
            cliente=instance.venta_reserva.cliente,
            tipo_movimiento=tipo,
            descripcion=descripcion
        )


@receiver(post_save, sender=ReservaProducto)
def registrar_movimiento_reserva_producto(sender, instance, created, **kwargs):
    if created:
        tipo = 'Añadido Producto a Venta/Reserva'
        descripcion = f"Se ha añadido {instance.cantidad} x {instance.producto.nombre} a la venta/reserva #{instance.venta_reserva.id}."
    else:
        tipo = 'Actualización de Producto en Venta/Reserva'
        descripcion = f"Se ha actualizado {instance.cantidad} x {instance.producto.nombre} en la venta/reserva #{instance.venta_reserva.id}."

    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )


@receiver(post_save, sender=ReservaServicio)
def registrar_movimiento_reserva_servicio(sender, instance, created, **kwargs):
    if created:
        tipo = 'Añadido Servicio a Venta/Reserva'
        descripcion = f"Se ha reservado el servicio {instance.servicio.nombre} para el {instance.fecha_agendamiento} en la venta/reserva #{instance.venta_reserva.id}."
    else:
        tipo = 'Actualización de Servicio en Venta/Reserva'
        descripcion = f"Se ha actualizado la reserva del servicio {instance.servicio.nombre} para el {instance.fecha_agendamiento} en la venta/reserva #{instance.venta_reserva.id}."

    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )


@receiver(post_delete, sender=ReservaProducto)
def registrar_movimiento_eliminacion_producto(sender, instance, **kwargs):
    tipo = 'Eliminación de Producto en Venta/Reserva'
    descripcion = f"Se ha eliminado {instance.cantidad} x {instance.producto.nombre} de la venta/reserva #{instance.venta_reserva.id}."

    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )


@receiver(post_delete, sender=ReservaServicio)
def registrar_movimiento_eliminacion_servicio(sender, instance, **kwargs):
    tipo = 'Eliminación de Servicio en Venta/Reserva'
    descripcion = f"Se ha eliminado la reserva del servicio {instance.servicio.nombre} de la venta/reserva #{instance.venta_reserva.id}."

    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

@receiver(post_save, sender=ReservaProducto)
@receiver(post_delete, sender=ReservaProducto)
def actualizar_total_reserva_producto(sender, instance, **kwargs):
    instance.venta_reserva.calcular_total()

@receiver(post_save, sender=ReservaServicio)
@receiver(post_delete, sender=ReservaServicio)
def actualizar_total_reserva_servicio(sender, instance, **kwargs):
    instance.venta_reserva.calcular_total()

@receiver(post_save, sender=Pago)
def actualizar_saldo_pago(sender, instance, **kwargs):
    instance.venta_reserva.actualizar_saldo()