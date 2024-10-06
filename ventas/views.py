
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import render
from datetime import datetime
from django.utils import timezone
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Cliente, Pago, CategoriaServicio, Servicio, ReservaServicio
from .utils import verificar_disponibilidad
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .serializers import (
    ProveedorSerializer,
    CategoriaProductoSerializer,
    ProductoSerializer,
    VentaReservaSerializer,
    ClienteSerializer,
    PagoSerializer,
    ReservaProductoSerializer,
    ServicioSerializer,
    ReservaServicioSerializer,
    CategoriaServicioSerializer,
    VentaReservaSerializer
)

def servicios_vendidos_view(request):
    # Obtener los parámetros del filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    categoria_id = request.GET.get('categoria')

    # Consultar todos los servicios vendidos
    servicios_vendidos = ReservaServicio.objects.select_related('venta_reserva__cliente', 'servicio__categoria')

    # Filtrar por rango de fechas si está presente
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        servicios_vendidos = servicios_vendidos.filter(fecha_agendamiento__gte=fecha_inicio)

    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        servicios_vendidos = servicios_vendidos.filter(fecha_agendamiento__lte=fecha_fin)

    # Filtrar por categoría de servicio si está presente
    if categoria_id:
        servicios_vendidos = servicios_vendidos.filter(servicio__categoria_id=categoria_id)

    # Ordenar primero por fecha en orden decreciente y luego por hora en orden creciente
    servicios_vendidos = servicios_vendidos.order_by('-fecha_agendamiento__date', 'fecha_agendamiento__time')

    # Obtener todas las categorías de servicio para el filtro
    categorias = CategoriaServicio.objects.all()

    # Preparar los datos para la tabla
    data = []
    for servicio in servicios_vendidos:
        total_monto = servicio.servicio.precio_base * servicio.cantidad_personas
        fecha_agendamiento = timezone.localtime(servicio.fecha_agendamiento)  # Convertir a hora local si es necesario

        data.append({
            'venta_reserva_id': servicio.venta_reserva.id,  # Número de venta/reserva
            'cliente_nombre': servicio.venta_reserva.cliente.nombre,  # Nombre del cliente
            'categoria_servicio': servicio.servicio.categoria.nombre,  # Categoría del servicio
            'servicio_nombre': servicio.servicio.nombre,  # Nombre del servicio
            'fecha_agendamiento': fecha_agendamiento.date(),  # Mostrar solo la fecha
            'hora_agendamiento': fecha_agendamiento.time(),  # Mostrar solo la hora
            'monto': servicio.servicio.precio_base,  # Monto por persona
            'cantidad_personas': servicio.cantidad_personas,  # Cantidad de pasajeros
            'total_monto': total_monto  # Monto total (monto * cantidad_personas)
        })

    # Pasar los datos y las categorías a la plantilla
    return render(request, 'ventas/servicios_vendidos.html', {
        'servicios': data,
        'categorias': categorias,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'categoria_id': categoria_id
    })

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


class CategoriaServicioViewSet(viewsets.ModelViewSet):
    queryset = CategoriaServicio.objects.all()
    serializer_class = CategoriaServicioSerializer


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

    def get_queryset(self):
        """
        Filtra las reservas por cliente, servicio, o fecha.
        """
        queryset = super().get_queryset()

        # Filtros por cliente, servicio y fecha
        cliente_id = self.request.query_params.get('cliente')
        servicio_id = self.request.query_params.get('servicio')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')

        # Filtrar por cliente
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)

        # Filtrar por servicio
        if servicio_id:
            queryset = queryset.filter(servicios__id=servicio_id)

        # Filtrar por rango de fechas
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(fecha_reserva__range=[fecha_inicio, fecha_fin])
        elif fecha_inicio:
            queryset = queryset.filter(fecha_reserva__gte=fecha_inicio)
        elif fecha_fin:
            queryset = queryset.filter(fecha_reserva__lte=fecha_fin)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        cliente_id = data.get('cliente')
        productos = data.get('productos')
        servicios = data.get('servicios')

        # Envolver en una transacción atómica
        with transaction.atomic():
            # Crear la venta/reserva
            venta_reserva = VentaReserva.objects.create(cliente_id=cliente_id)

            # Procesar los productos (sin lógica de reserva)
            for producto_data in productos:
                producto_id = producto_data.get('producto')
                cantidad = producto_data.get('cantidad')
                producto = Producto.objects.get(id=producto_id)

                # Verificar si hay inventario suficiente
                if producto.cantidad_disponible < cantidad:
                    raise ValidationError(f"No hay suficiente inventario para el producto {producto.nombre}.")

                # Reducir inventario y agregar producto a la reserva
                producto.reducir_inventario(cantidad)
                venta_reserva.agregar_producto(producto, cantidad)

            # Procesar los servicios (con lógica de reserva)
            for servicio_data in servicios:
                servicio_id = servicio_data.get('servicio')
                fecha_agendamiento = servicio_data.get('fecha_agendamiento')
                servicio = Servicio.objects.get(id=servicio_id)

                # Verificar disponibilidad del servicio
                if not verificar_disponibilidad(servicio, fecha_agendamiento, fecha_agendamiento + servicio.duracion):
                    raise ValidationError(f"El servicio {servicio.nombre} no está disponible en el horario solicitado.")

                # Agregar el servicio a la reserva
                venta_reserva.agregar_servicio(servicio, fecha_agendamiento)

            # Guardar la reserva y calcular el total
            venta_reserva.calcular_total()
            venta_reserva.save()

        # Serializar la respuesta con los datos actualizados
        serializer = self.get_serializer(venta_reserva)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        # Procesar los productos actualizados (sin lógica de reserva)
        productos = data.get('productos', [])
        for producto_data in productos:
            producto_id = producto_data.get('producto')
            cantidad = producto_data.get('cantidad')
            producto = Producto.objects.get(id=producto_id)

            # Verificar si hay inventario suficiente antes de agregar
            if producto.cantidad_disponible < cantidad:
                raise ValidationError(f"No hay suficiente inventario para el producto {producto.nombre}.")

            instance.agregar_producto(producto, cantidad)

        # Procesar los servicios actualizados (con lógica de reserva)
        servicios = data.get('servicios', [])
        for servicio_data in servicios:
            servicio_id = servicio_data.get('servicio')
            fecha_agendamiento = servicio_data.get('fecha_agendamiento')
            servicio = Servicio.objects.get(id=servicio_id)

            # Verificar disponibilidad del servicio
            if not verificar_disponibilidad(servicio, fecha_agendamiento, fecha_agendamiento + servicio.duracion):
                raise ValidationError(f"El servicio {servicio.nombre} no está disponible en el horario solicitado.")

            instance.agregar_servicio(servicio, fecha_agendamiento)

        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        venta_reserva_id = data.get('venta_reserva')
        monto = data.get('monto')
        metodo_pago = data.get('metodo_pago')

        venta_reserva = VentaReserva.objects.get(id=venta_reserva_id)

        pago = Pago.objects.create(
            venta_reserva=venta_reserva,
            monto=monto,
            metodo_pago=metodo_pago,
            fecha_pago=timezone.now()
        )

        venta_reserva.pagado += pago.monto
        venta_reserva.saldo_pendiente = venta_reserva.total - venta_reserva.pagado

        if venta_reserva.saldo_pendiente <= 0:
            venta_reserva.estado = 'pagado'
        elif 0 < venta_reserva.saldo_pendiente < venta_reserva.total:
            venta_reserva.estado = 'parcial'
        else:
            venta_reserva.estado = 'pendiente'

        venta_reserva.save()

        serializer = self.get_serializer(pago)
        return Response(serializer.data)

def inicio_sistema_view(request):
    """
    Vista que renderiza la página de inicio del sistema con enlaces a los recursos importantes.
    """
    return render(request, 'ventas/inicio_sistema.html')

def auditoria_movimientos_view(request):
    # Obtener parámetros de fecha de inicio y fin desde el formulario GET
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Convertir las fechas desde cadenas a objetos datetime
    if fecha_inicio:
        fecha_inicio = parse_date(fecha_inicio)
    if fecha_fin:
        fecha_fin = parse_date(fecha_fin)

    # Filtrar los movimientos por rango de fechas
    movimientos = MovimientoCliente.objects.all()
    
    if fecha_inicio and fecha_fin:
        movimientos = movimientos.filter(fecha__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        movimientos = movimientos.filter(fecha__gte=fecha_inicio)
    elif fecha_fin:
        movimientos = movimientos.filter(fecha__lte=fecha_fin)

    # Pasar los movimientos y las fechas al contexto
    context = {
        'movimientos': movimientos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }

    return render(request, 'ventas/auditoria_movimientos.html', context)

def caja_diaria_view(request):
    # Obtener la fecha actual
    hoy = timezone.now().date()

    # Filtrar los pagos realizados hoy y agruparlos por método de pago
    pagos_por_metodo = Pago.objects.filter(fecha_pago__date=hoy).values('metodo_pago').annotate(total=Sum('monto'))

    # Calcular el total general del día
    total_dia = pagos_por_metodo.aggregate(Sum('total'))['total__sum'] or 0

    # Pasar los datos a la plantilla
    context = {
        'pagos_por_metodo': pagos_por_metodo,
        'total_dia': total_dia,
        'fecha': hoy,
    }

    return render(request, 'ventas/caja_diaria.html', context)