from rest_framework import serializers
from .models import Proveedor, CategoriaProducto, Producto, Reserva, Venta, Pago, Cliente, ReservaProducto

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

class ReservaProductoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()

    class Meta:
        model = ReservaProducto
        fields = ['producto', 'cantidad']

class ReservaSerializer(serializers.ModelSerializer):
    productos = ReservaProductoSerializer(source='reservaprodutos', many=True)
    cliente = serializers.StringRelatedField()
    pagos = serializers.StringRelatedField(many=True)

    class Meta:
        model = Reserva
        fields = ['id', 'cliente', 'productos', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado', 'pagos']

class VentaSerializer(serializers.ModelSerializer):
    pagos = serializers.StringRelatedField(many=True)
    cliente = serializers.StringRelatedField()

    class Meta:
        model = Venta
        fields = ['id', 'cliente', 'total', 'pagado', 'saldo_pendiente', 'fecha_venta', 'pagos']

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
