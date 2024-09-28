from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import VentaReserva, Pago, Cliente, ReservaProducto

@receiver(post_save, sender=VentaReserva)
def registrar_movimiento_venta(sender, instance, created, **kwargs):
    if created:
        instance.calcular_total()

@receiver(post_save, sender=Pago)
def actualizar_pago_venta(sender, instance, **kwargs):
    instance.venta_reserva.actualizar_pago()

@receiver(post_save, sender=ReservaProducto)
def actualizar_total_reserva(sender, instance, **kwargs):
    instance.venta_reserva.calcular_total()
