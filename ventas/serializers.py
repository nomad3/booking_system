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
        ('webpay', 'WebPay'),
    ]

    metodo_pago = serializers.ChoiceField(choices=METODOS_PAGO)

    class Meta:
        model = Pago
        fields = ['id', 'venta_reserva', 'fecha_pago', 'monto', 'metodo_pago']
        read_only_fields = ['venta_reserva', 'fecha_pago']


class VentaReservaSerializer(serializers.ModelSerializer):
    pagos = PagoSerializer(many=True, read_only=True)
    productos = ReservaProductoSerializer(many=True)  # Los productos no son read-only
    servicios = ReservaServicioSerializer(many=True, read_only=True, source='reservaservicios')
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    pagado = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    saldo_pendiente = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = VentaReserva
        fields = ['id', 'cliente', 'productos', 'servicios', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado', 'pagos']
        read_only_fields = ['total', 'pagado', 'saldo_pendiente']

    def create(self, validated_data):
        productos_data = validated_data.pop('productos', [])
        venta_reserva = VentaReserva.objects.create(**validated_data)

        # Procesar los productos vendidos
        for producto_data in productos_data:
            producto = producto_data['producto']
            cantidad = producto_data['cantidad']

            # Reducir el inventario
            producto.reducir_inventario(cantidad)

            # Registrar la venta del producto
            ReservaProducto.objects.create(venta_reserva=venta_reserva, producto=producto, cantidad=cantidad)

        # Calcular el total después de agregar productos
        venta_reserva.calcular_total()
        return venta_reserva

    def update(self, instance, validated_data):
        productos_data = validated_data.pop('productos', [])
        
        # Procesar los productos vendidos (esto puede involucrar reducir más inventario o modificar)
        for producto_data in productos_data:
            producto = producto_data['producto']
            cantidad = producto_data['cantidad']

            # Reducir el inventario
            producto.reducir_inventario(cantidad)

            # Actualizar la venta del producto
            ReservaProducto.objects.update_or_create(venta_reserva=instance, producto=producto, defaults={'cantidad': cantidad})

        # Calcular el total después de actualizar productos
        instance.calcular_total()
        return instance