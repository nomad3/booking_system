from rest_framework import viewsets
from rest_framework.response import Response
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, ReservaServicio, Cliente, Pago, Servicio
from .serializers import (
    ProveedorSerializer,
    CategoriaProductoSerializer,
    ProductoSerializer,
    ServicioSerializer,
    VentaReservaSerializer,
    ClienteSerializer,
    PagoSerializer,
    ReservaProductoSerializer,
    ReservaServicioSerializer
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


class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer


class ReservaProductoViewSet(viewsets.ModelViewSet):
    queryset = ReservaProducto.objects.all()
    serializer_class = ReservaProductoSerializer


class ReservaServicioViewSet(viewsets.ModelViewSet):
    queryset = ReservaServicio.objects.all()
    serializer_class = ReservaServicioSerializer


class VentaReservaViewSet(viewsets.ModelViewSet):
    queryset = VentaReserva.objects.all()
    serializer_class = VentaReservaSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        cliente_id = data.get('cliente')
        productos_data = data.get('productos', [])
        servicios_data = data.get('servicios', [])
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
            ReservaProducto.objects.create(venta_reserva=venta_reserva, producto=producto, cantidad=cantidad)

        # Add services to the VentaReserva
        for servicio_data in servicios_data:
            servicio_id = servicio_data.get('servicio')
            fecha_agendamiento = servicio_data.get('fecha_agendamiento')
            servicio = Servicio.objects.get(id=servicio_id)
            ReservaServicio.objects.create(venta_reserva=venta_reserva, servicio=servicio, fecha_agendamiento=fecha_agendamiento)

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
