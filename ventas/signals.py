from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import VentaReserva, Pago, ReservaProducto


# Signal to handle payments and update VentaReserva status
@receiver(post_save, sender=Pago)
def actualizar_estado_pago(sender, instance, created, **kwargs):
    if created:
        instance.venta_reserva.actualizar_pago()


# Signal to recalculate the total when a new product is added to the reservation
@receiver(post_save, sender=ReservaProducto)
def actualizar_total_reserva(sender, instance, created, **kwargs):
    if created:
        instance.venta_reserva.calcular_total()


# Signal to handle product removal and update the total
@receiver(post_delete, sender=ReservaProducto)
def actualizar_total_reserva_al_eliminar(sender, instance, **kwargs):
    instance.venta_reserva.calcular_total()
