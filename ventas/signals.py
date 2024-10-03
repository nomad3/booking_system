from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import VentaReserva, Cliente, ReservaProducto, ReservaServicio, Pago, MovimientoCliente

# Señales para la auditoría de ventas, pagos y clientes

@receiver(post_save, sender=VentaReserva)
def registrar_movimiento_venta(sender, instance, created, **kwargs):
    tipo = 'Creación de Venta/Reserva' if created else 'Actualización de Venta/Reserva'
    descripcion = f"Se ha {'creado' if created else 'actualizado'} la venta/reserva con ID {instance.id} para el cliente {instance.cliente.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

@receiver(post_delete, sender=VentaReserva)
def registrar_movimiento_eliminacion_venta(sender, instance, **kwargs):
    descripcion = f"Se ha eliminado la venta/reserva con ID {instance.id} del cliente {instance.cliente.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento='Eliminación de Venta/Reserva',
        descripcion=descripcion
    )

# Clientes

@receiver(post_save, sender=Cliente)
def registrar_movimiento_cliente(sender, instance, created, **kwargs):
    descripcion = f"Se ha {'creado' if created else 'actualizado'} el cliente: {instance.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance,
        tipo_movimiento='Creación de Cliente' if created else 'Actualización de Cliente',
        descripcion=descripcion
    )

@receiver(post_delete, sender=Cliente)
def registrar_movimiento_eliminacion_cliente(sender, instance, **kwargs):
    descripcion = f"Se ha eliminado el cliente: {instance.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance,
        tipo_movimiento='Eliminación de Cliente',
        descripcion=descripcion
    )

# Productos

@receiver(post_save, sender=ReservaProducto)
def registrar_movimiento_reserva_producto(sender, instance, created, **kwargs):
    tipo = 'Añadido Producto a Venta/Reserva' if created else 'Actualización de Producto en Venta/Reserva'
    descripcion = f"Se ha {'añadido' if created else 'actualizado'} {instance.cantidad} x {instance.producto.nombre} en la venta/reserva #{instance.venta_reserva.id}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

@receiver(post_delete, sender=ReservaProducto)
def registrar_movimiento_eliminacion_producto(sender, instance, **kwargs):
    descripcion = f"Se ha eliminado {instance.cantidad} x {instance.producto.nombre} de la venta/reserva #{instance.venta_reserva.id}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento='Eliminación de Producto en Venta/Reserva',
        descripcion=descripcion
    )

# Servicios

@receiver(post_save, sender=ReservaServicio)
def registrar_movimiento_reserva_servicio(sender, instance, created, **kwargs):
    tipo = 'Añadido Servicio a Venta/Reserva' if created else 'Actualización de Servicio en Venta/Reserva'
    descripcion = f"Se ha {'reservado' if created else 'actualizado'} el servicio {instance.servicio.nombre} para el {instance.fecha_agendamiento} en la venta/reserva #{instance.venta_reserva.id}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

@receiver(post_delete, sender=ReservaServicio)
def registrar_movimiento_eliminacion_servicio(sender, instance, **kwargs):
    descripcion = f"Se ha eliminado la reserva del servicio {instance.servicio.nombre} de la venta/reserva #{instance.venta_reserva.id}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento='Eliminación de Servicio en Venta/Reserva',
        descripcion=descripcion
    )

# Pagos

@receiver(post_save, sender=Pago)
def registrar_movimiento_pago(sender, instance, created, **kwargs):
    tipo = 'Pago Realizado' if created else 'Actualización de Pago'
    descripcion = f"Se ha {'registrado' if created else 'actualizado'} un pago de {instance.monto} para la venta/reserva #{instance.venta_reserva.id} mediante {instance.metodo_pago}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion
    )

    # Actualizar el saldo de la venta después de un nuevo pago
    if created:
        instance.venta_reserva.pagado += instance.monto
        instance.venta_reserva.actualizar_saldo()

@receiver(post_delete, sender=Pago)
def registrar_movimiento_eliminacion_pago(sender, instance, **kwargs):
    descripcion = f"Se ha eliminado el pago de {instance.monto} de la venta/reserva #{instance.venta_reserva.id}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento='Eliminación de Pago',
        descripcion=descripcion
    )

    # Restar el pago eliminado y actualizar el saldo pendiente
    instance.venta_reserva.pagado -= instance.monto
    if instance.venta_reserva.pagado < 0:
        instance.venta_reserva.pagado = 0  # Evitar valores negativos
    instance.venta_reserva.actualizar_saldo()

# Actualización automática del total y saldo pendiente cuando se añaden o eliminan productos, servicios y pagos
@receiver(post_save, sender=ReservaProducto)
@receiver(post_delete, sender=ReservaProducto)
def actualizar_total_reserva_producto(sender, instance, **kwargs):
    instance.venta_reserva.calcular_total()

@receiver(post_save, sender=ReservaServicio)
@receiver(post_delete, sender=ReservaServicio)
def actualizar_total_reserva_servicio(sender, instance, **kwargs):
    instance.venta_reserva.calcular_total()

@receiver(post_save, sender=Pago)
def actualizar_monto_y_registrar_movimiento_pago_creado(sender, instance, created, **kwargs):
    if created:
        # Actualizar el saldo pendiente
        instance.venta_reserva.pagado += instance.monto
        instance.venta_reserva.actualizar_saldo()
