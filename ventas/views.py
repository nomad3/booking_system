from rest_framework import viewsets
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Pago, Cliente
from .serializers import ProveedorSerializer, CategoriaProductoSerializer, ProductoSerializer, VentaReservaSerializer, ReservaProductoSerializer, PagoSerializer, ClienteSerializer

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class VentaReservaViewSet(viewsets.ModelViewSet):
    queryset = VentaReserva.objects.all()
    serializer_class = VentaReservaSerializer

class ReservaProductoViewSet(viewsets.ModelViewSet):
    queryset = ReservaProducto.objects.all()
    serializer_class = ReservaProductoSerializer

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
