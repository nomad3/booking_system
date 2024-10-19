from django.db.models.signals import pre_delete, post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from django.apps import apps
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
def actualizar_total_al_guardar_servicio(sender, instance, created, raw, using, update_fields, **kwargs):  # Agrega raw y using
    if created:
        instance.venta_reserva.calcular_total()
    elif not raw:  # Verifica que no sea una creación raw
        try:
            anterior_reserva_servicio = ReservaServicio.objects.using(using).get(pk=instance.pk)
            if anterior_reserva_servicio.cantidad_personas != instance.cantidad_personas or anterior_reserva_servicio.servicio != instance.servicio:
                instance.venta_reserva.calcular_total()
        except ReservaServicio.DoesNotExist:
            pass  # La instancia no existía antes, probablemente creada a través del inline

@receiver(post_save, sender=ReservaProducto)
@receiver(post_save, sender=ReservaServicio)
def actualizar_total_venta_reserva(sender, instance, created, **kwargs):
    instance.venta_reserva.actualizar_total()
    instance.venta_reserva.save() # Guardar los cambios del total

@receiver(post_save, sender=ReservaProducto)
def actualizar_inventario(sender, instance, created, raw, using, update_fields, **kwargs):
    if created and not raw: #previene error si se importa una reserva que tiene productos
        with transaction.atomic():
            instance.producto.reducir_inventario(instance.cantidad)

    elif not raw: # and not created: #Si se modifica la reserva que ya existe
        ReservaProducto = apps.get_model('ventas', 'ReservaProducto')
        try:
            reserva_producto_anterior = ReservaProducto.objects.using(using).get(pk=instance.pk)
            cantidad_anterior = reserva_producto_anterior.cantidad

        except ReservaProducto.DoesNotExist:
            return # retorna para evitar el error cuando recien se crea el modelo de ReservaProducto

        diferencia = instance.cantidad - cantidad_anterior

        with transaction.atomic():
            if diferencia > 0:
                instance.producto.reducir_inventario(diferencia)

            elif diferencia < 0:
                instance.producto.cantidad_disponible += abs(diferencia) #Suma la diferencia, si la cantidad disminuye la diferencia es negativa, se convierte en positivo y se suma al inventario
                instance.producto.save()

@receiver(post_save, sender=ReservaProducto)
def actualizar_inventario_post_save(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        with transaction.atomic():
            instance.producto.reducir_inventario(instance.cantidad)
    elif not raw and instance.tracker.has_changed('cantidad'):
        with transaction.atomic():
            cantidad_anterior = instance.tracker.previous('cantidad')
            if cantidad_anterior is not None:
                diferencia = instance.cantidad - cantidad_anterior
                if diferencia > 0:
                    instance.producto.reducir_inventario(diferencia)
                elif diferencia < 0:
                    instance.producto.cantidad_disponible -= diferencia
                    instance.producto.save()

@receiver(pre_delete, sender=ReservaProducto)
def restaurar_inventario(sender, instance, **kwargs):
    with transaction.atomic():
        instance.producto.cantidad_disponible += instance.cantidad
        instance.producto.save()

@receiver(post_save, sender=ReservaProducto)  # Signal para actualizar inventario y total
def actualizar_inventario_y_total(sender, instance, created, raw, using, update_fields, **kwargs):
    if created and not raw:
        with transaction.atomic():
            instance.producto.reducir_inventario(instance.cantidad)
            instance.venta_reserva.calcular_total() # Actualiza el total de la VentaReserva
    elif not raw and instance.tracker.has_changed('cantidad'):
        with transaction.atomic():
            cantidad_anterior = instance.tracker.previous('cantidad')
            if cantidad_anterior is not None:
                diferencia = instance.cantidad - cantidad_anterior
                if diferencia > 0:
                    instance.producto.reducir_inventario(diferencia)
                elif diferencia < 0:
                    instance.producto.cantidad_disponible += abs(diferencia)
                    instance.producto.save()
            instance.venta_reserva.calcular_total() # Actualiza el total de la VentaReserva

@receiver(pre_delete, sender=ReservaProducto)  # Signal para restaurar inventario y total
def restaurar_inventario_y_total(sender, instance, **kwargs):
    with transaction.atomic():
        instance.producto.cantidad_disponible += instance.cantidad
        instance.producto.save()
        instance.venta_reserva.calcular_total() # Actualiza el total de la VentaReserva

@receiver(m2m_changed, sender=VentaReserva.productos.through)  # Signal para cuando se eliminan mediante m2m
def actualizar_inventario_m2m(sender, instance, action, **kwargs):
    if action in ('post_remove', 'post_clear'):  # Restaurar inventario al eliminar productos de VentaReserva
        if kwargs.get('pk_set'):
            for pk in kwargs['pk_set']:
                try:
                    producto = Producto.objects.get(pk=pk)
                    reserva_producto = ReservaProducto.objects.get(venta_reserva=instance, producto=producto)
                    cantidad = reserva_producto.cantidad
                    producto.cantidad_disponible += cantidad
                    producto.save()
                except ReservaProducto.DoesNotExist:
                    pass