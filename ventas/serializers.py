from rest_framework import serializers
from .models import Proveedor, CategoriaProducto, Producto, Servicio, VentaReserva, Cliente, Pago, ReservaProducto, ReservaServicio


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'


class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'


class ReservaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaProducto
        fields = '__all__'


class ReservaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaServicio
        fields = '__all__'


class VentaReservaSerializer(serializers.ModelSerializer):
    productos = ReservaProductoSerializer(many=True, read_only=True, source='reservaproductos')
    servicios = ReservaServicioSerializer(many=True, read_only=True, source='reservaservicios')
    pagos = PagoSerializer(many=True, read_only=True)

    class Meta:
        model = VentaReserva
        fields = '__all__'
