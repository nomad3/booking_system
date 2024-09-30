from rest_framework import serializers
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, Cliente, Pago, ReservaProducto, CategoriaServicio, Servicio, ReservaServicio


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


class CategoriaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaServicio
        fields = '__all__'


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class ReservaProductoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)

    class Meta:
        model = ReservaProducto
        fields = '__all__'


class ReservaServicioSerializer(serializers.ModelSerializer):
    servicio = ServicioSerializer(read_only=True)

    class Meta:
        model = ReservaServicio
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    METODOS_PAGO = [
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
    ]

    metodo_pago = serializers.ChoiceField(choices=METODOS_PAGO)

    class Meta:
        model = Pago
        fields = ['id', 'venta_reserva', 'fecha_pago', 'monto', 'metodo_pago']
        read_only_fields = ['venta_reserva', 'fecha_pago']


class VentaReservaSerializer(serializers.ModelSerializer):
    pagos = PagoSerializer(many=True, read_only=True)
    productos = ReservaProductoSerializer(many=True, read_only=True, source='reservaprodutos')
    servicios = ReservaServicioSerializer(many=True, read_only=True, source='reservaservicios')
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    pagado = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    saldo_pendiente = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = VentaReserva
        fields = ['id', 'cliente', 'productos', 'servicios', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado', 'pagos']
        read_only_fields = ['total', 'pagado', 'saldo_pendiente']
