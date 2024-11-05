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
    class Meta:
        model = ReservaProducto
        fields = ['producto', 'cantidad']

    def create(self, validated_data):
        producto = validated_data['producto']
        cantidad = validated_data['cantidad']

        # Reducir inventario durante la creación del producto
        producto.reducir_inventario(cantidad)

        return super().create(validated_data)

class ReservaServicioSerializer(serializers.ModelSerializer):
    servicio = ServicioSerializer(read_only=True)
    estado = serializers.ChoiceField(choices=ReservaServicio.ESTADO_CHOICES)

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
    usuario = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Pago
        fields = ['id', 'venta_reserva', 'fecha_pago', 'monto', 'metodo_pago', 'usuario', 'giftcard']
        read_only_fields = ['venta_reserva', 'fecha_pago']


class VentaReservaSerializer(serializers.ModelSerializer):
    pagos = PagoSerializer(many=True, read_only=True)
    productos = ReservaProductoSerializer(many=True, source='reservaproductos')
    servicios = ReservaServicioSerializer(many=True, read_only=True, source='reservaservicios')
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    pagado = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    saldo_pendiente = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    numero_documento_fiscal = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = VentaReserva
        fields = ['id', 'cliente', 'productos', 'servicios', 'fecha_reserva', 'total', 'pagado', 'saldo_pendiente', 'estado', 'pagos', 'numero_documento_fiscal']
        read_only_fields = ['total', 'pagado', 'saldo_pendiente']

    def create(self, validated_data):
        productos_data = validated_data.pop('productos', [])
        venta_reserva = VentaReserva.objects.create(**validated_data)

        # Procesar los productos vendidos
        for producto_data in productos_data:
            producto = producto_data['producto']
            cantidad = producto_data['cantidad']

            # Crear la relación producto-venta y reducir inventario
            ReservaProducto.objects.create(venta_reserva=venta_reserva, producto=producto, cantidad=cantidad)
            producto.reducir_inventario(cantidad)  # Reducir inventario

        # Calcular el total después de agregar productos
        venta_reserva.calcular_total()
        return venta_reserva

    def update(self, instance, validated_data):
        productos_data = validated_data.pop('productos', [])
        
        # Procesar los productos vendidos
        for producto_data in productos_data:
            producto = producto_data['producto']
            cantidad = producto_data['cantidad']

            # Actualizar la relación producto-venta y reducir inventario
            ReservaProducto.objects.update_or_create(venta_reserva=instance, producto=producto, defaults={'cantidad': cantidad})
            producto.reducir_inventario(cantidad)  # Reducir inventario

        # Calcular el total después de actualizar productos
        instance.calcular_total()
        return instance
