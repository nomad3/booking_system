from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from .models import VentaReserva, Cliente, ReservaProducto, ReservaServicio, Pago, MovimientoCliente
from django.contrib.auth.models import User  # Importa el modelo de usuario
from .middleware import get_current_user  # Importa el middleware

# Movimientos y auditoría

@receiver(post_save, sender=VentaReserva)
def registrar_movimiento_venta(sender, instance, created, **kwargs):
    usuario = get_current_user()
    tipo = 'Creación de Venta/Reserva' if created else 'Actualización de Venta/Reserva'
    descripcion = f"Se ha {'creado' if created else 'actualizado'} la venta/reserva con ID {instance.id} para el cliente {instance.cliente.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion,
        usuario=usuario,
        fecha_movimiento=timezone.now()
    )

@receiver(post_delete, sender=VentaReserva)
def registrar_movimiento_eliminacion_venta(sender, instance, **kwargs):
    usuario = get_current_user()
    descripcion = f"Se ha eliminado la venta/reserva con ID {instance.id} del cliente {instance.cliente.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance.cliente,
        tipo_movimiento='Eliminación de Venta/Reserva',
        descripcion=descripcion,
        usuario=usuario,
        fecha_movimiento=timezone.now()
    )

# Clientes

@receiver(post_save, sender=Cliente)
def registrar_movimiento_cliente(sender, instance, created, **kwargs):
    usuario = get_current_user()
    descripcion = f"Se ha {'creado' if created else 'actualizado'} el cliente: {instance.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance,
        tipo_movimiento='Creación de Cliente' if created else 'Actualización de Cliente',
        descripcion=descripcion,
        usuario=usuario,
        fecha_movimiento=timezone.now()
    )

@receiver(post_delete, sender=Cliente)
def registrar_movimiento_eliminacion_cliente(sender, instance, **kwargs):
    usuario = get_current_user()
    descripcion = f"Se ha eliminado el cliente: {instance.nombre}."
    
    MovimientoCliente.objects.create(
        cliente=instance,
        tipo_movimiento='Eliminación de Cliente',
        descripcion=descripcion,
        usuario=usuario,
        fecha_movimiento=timezone.now()
    )

# Productos

@receiver(post_save, sender=ReservaProducto)
def registrar_movimiento_reserva_producto(sender, instance, created, **kwargs):
    usuario = get_current_user()
    tipo = 'Añadido Producto a Venta/Reserva' if created else 'Actualización de Producto en Venta/Reserva'
    descripcion = f"Se ha {'añadido' if created else 'actualizado'} {instance.cantidad} x {instance.producto.nombre} en la venta/reserva #{instance.venta_reserva.id}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion,
        usuario=usuario,
        fecha_movimiento=timezone.now()
    )

@receiver(post_delete, sender=ReservaProducto)
def registrar_movimiento_eliminacion_producto(sender, instance, **kwargs):
    usuario = get_current_user()
    descripcion = f"Se ha eliminado {instance.cantidad} x {instance.producto.nombre} de la venta/reserva #{instance.venta_reserva.id}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento='Eliminación de Producto en Venta/Reserva',
        descripcion=descripcion,
        usuario=usuario,
        fecha_movimiento=timezone.now()
    )

# Servicios

@receiver(post_save, sender=ReservaServicio)
def registrar_movimiento_reserva_servicio(sender, instance, created, **kwargs):
    usuario = get_current_user()
    tipo = 'Añadido Servicio a Venta/Reserva' if created else 'Actualización de Servicio en Venta/Reserva'
    descripcion = f"Se ha {'reservado' if created else 'actualizado'} el servicio {instance.servicio.nombre} para el {instance.fecha_agendamiento} en la venta/reserva #{instance.venta_reserva.id}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion,
        usuario=usuario,
        fecha_movimiento=timezone.now()
    )

@receiver(post_delete, sender=ReservaServicio)
def registrar_movimiento_eliminacion_servicio(sender, instance, **kwargs):
    usuario = get_current_user()
    descripcion = f"Se ha eliminado la reserva del servicio {instance.servicio.nombre} de la venta/reserva #{instance.venta_reserva.id}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento='Eliminación de Servicio en Venta/Reserva',
        descripcion=descripcion,
        usuario=usuario,
        fecha_movimiento=timezone.now()
    )

# Pagos

@receiver(post_save, sender=Pago)
def registrar_movimiento_pago(sender, instance, created, **kwargs):
    usuario = get_current_user()
    tipo = 'Pago Realizado' if created else 'Actualización de Pago'
    descripcion = f"Se ha {'registrado' if created else 'actualizado'} un pago de {instance.monto} para la venta/reserva #{instance.venta_reserva.id} mediante {instance.metodo_pago}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento=tipo,
        descripcion=descripcion,
        usuario=usuario,
        fecha_movimiento=timezone.now()
    )

   # NO necesitas actualizar el saldo aquí. Ya se hace en el save() de Pago.

@receiver(post_delete, sender=Pago)
def registrar_movimiento_eliminacion_pago(sender, instance, **kwargs):
    usuario = get_current_user()
    descripcion = f"Se ha eliminado el pago de {instance.monto} de la venta/reserva #{instance.venta_reserva.id}."
    
    MovimientoCliente.objects.create(
        cliente=instance.venta_reserva.cliente,
        tipo_movimiento='Eliminación de Pago',
        descripcion=descripcion,
        usuario=usuario,
        fecha_movimiento=timezone.now()
    )

    # Restar el pago eliminado y actualizar el saldo pendiente
    instance.venta_reserva.pagado -= instance.monto
    instance.venta_reserva.actualizar_saldo()
    instance.venta_reserva.calcular_total()  # Recalcular el total

@receiver(post_delete, sender=ReservaProducto)
def actualizar_total_al_eliminar_producto(sender, instance, **kwargs):
    instance.venta_reserva.calcular_total()

@receiver(post_delete, sender=ReservaServicio)
def actualizar_total_al_eliminar_servicio(sender, instance, **kwargs):
    instance.venta_reserva.calcular_total()

@receiver(post_save, sender=ReservaServicio)
def actualizar_total_al_guardar_servicio(sender, instance, created, **kwargs):
    if created or instance.cantidad_personas_changed():
        instance.venta_reserva.calcular_total()

@receiver(post_save, sender=ReservaProducto)
@receiver(post_save, sender=ReservaServicio)
def actualizar_total_venta_reserva(sender, instance, created, **kwargs):
    instance.venta_reserva.actualizar_total()
    instance.venta_reserva.save() # Guardar los cambios del total

@receiver(post_save, sender=ReservaProducto)
def actualizar_inventario(sender, instance, created, **kwargs):
    if created:  # Solo descuenta si es una nueva ReservaProducto
        instance.producto.reducir_inventario(instance.cantidad)
    elif instance.cantidad_changed():  # Si cambia la cantidad de un producto ya reservado
        cantidad_anterior = instance.tracker.previous('cantidad')  # Obtén la cantidad anterior
        if cantidad_anterior is not None:  # Manejo para la creación (no hay cantidad anterior)
            diferencia = instance.cantidad - cantidad_anterior
            if diferencia > 0:
                instance.producto.reducir_inventario(diferencia)
            elif diferencia < 0:
                instance.producto.cantidad_disponible -= diferencia # Suma al inventario si la cantidad se reduce
                instance.producto.save()

@receiver(m2m_changed, sender=VentaReserva.productos.through)
def actualizar_inventario_m2m(sender, instance, action, **kwargs):
    if action == 'post_add':
        for pk in kwargs['pk_set']:
            producto = Producto.objects.get(pk=pk)
            cantidad = ReservaProducto.objects.get(venta_reserva=instance, producto=producto).cantidad
            producto.reducir_inventario(cantidad)
    elif action == 'post_remove':  # Restaurar inventario al eliminar productos
        for pk in kwargs['pk_set']:
            producto = Producto.objects.get(pk=pk)
            cantidad = ReservaProducto.objects.filter(venta_reserva=instance, producto=producto).first().cantidad
            producto.cantidad_disponible += cantidad
            producto.save()
    elif action == 'post_clear':  # Restaurar inventario al borrar todos los productos
        for reserva_producto in ReservaProducto.objects.filter(venta_reserva=instance):
            reserva_producto.producto.cantidad_disponible += reserva_producto.cantidad
            reserva_producto.producto.save()