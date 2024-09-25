from rest_framework import serializers
from .models import Proveedor, CategoriaProducto, Producto, Reserva, Venta

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    precio_actual = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = '__all__'

    def get_precio_actual(self, obj):
        return obj.obtener_precio_actual()

class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'
