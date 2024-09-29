from rest_framework import viewsets
from rest_framework.response import Response
from django.utils import timezone
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Cliente, Pago
from .serializers import (
    ProveedorSerializer,
    CategoriaProductoSerializer,
    ProductoSerializer,
    VentaReservaSerializer,
    ClienteSerializer,
    PagoSerializer,
    ReservaProductoSerializer
)


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer


class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer


class ReservaProductoViewSet(viewsets.ModelViewSet):
    queryset = ReservaProducto.objects.all()
    serializer_class = ReservaProductoSerializer


class VentaReservaViewSet(viewsets.ModelViewSet):
    queryset = VentaReserva.objects.all()
    serializer_class = VentaReservaSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        cliente_id = data.get('cliente')
        productos_data = data.get('productos', [])
        fecha_reserva = data.get('fecha_reserva')

        # Get the client instance
        cliente = Cliente.objects.get(id=cliente_id)

        # Create the VentaReserva
        venta_reserva = VentaReserva.objects.create(
            cliente=cliente,
            fecha_reserva=fecha_reserva
        )

        # Add products to the VentaReserva
        for producto_data in productos_data:
            producto_id = producto_data.get('producto')
            cantidad = producto_data.get('cantidad', 1)
            producto = Producto.objects.get(id=producto_id)
            venta_reserva.agregar_producto(producto, cantidad)

        venta_reserva.calcular_total()
        venta_reserva.save()

        serializer = self.get_serializer(venta_reserva)
        return Response(serializer.data)


class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        venta_reserva_id = data.get('venta_reserva')
        monto = data.get('monto')
        metodo_pago = data.get('metodo_pago')

        # Get the VentaReserva instance
        venta_reserva = VentaReserva.objects.get(id=venta_reserva_id)

        # Create the Pago
        pago = Pago.objects.create(
            venta_reserva=venta_reserva,
            monto=monto,
            metodo_pago=metodo_pago
        )

        venta_reserva.actualizar_pago()
        venta_reserva.save()

        serializer = self.get_serializer(pago)
        return Response(serializer.data)
