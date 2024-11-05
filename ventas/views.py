from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Sum, Q, Count
from django.contrib.auth.decorators import user_passes_test
import csv
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Proveedor, CategoriaProducto, Producto, VentaReserva, ReservaProducto, Cliente, Pago, CategoriaServicio, Servicio, ReservaServicio, MovimientoCliente  
from .utils import verificar_disponibilidad
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_date
from django.db.models import Q, Sum
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
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
from .forms import ReservaServicioInlineForm

def venta_reserva_list(request):
    # Get current date
    today = timezone.localdate()

    # Get filters from GET parameters
    categoria_servicio_id = request.GET.get('categoria_servicio')
    servicio_id = request.GET.get('servicio')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # If fecha_inicio or fecha_fin are not provided, set them to today's date
    if not fecha_inicio:
        fecha_inicio = today.strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = today.strftime('%Y-%m-%d')

    # Parse the date strings to date objects with timezone awareness
    fecha_inicio_parsed = timezone.make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
    fecha_fin_parsed = timezone.make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d')) + timedelta(days=1)

    # Build the queryset with select_related and prefetch_related
    qs = VentaReserva.objects.select_related('cliente').prefetch_related(
        'reservaservicios__servicio',
        'reservaproductos__producto',
    )

    # Apply date range filter (inclusive of the end date)
    qs = qs.filter(fecha_reserva__range=(fecha_inicio_parsed, fecha_fin_parsed))

    # Apply filters based on category and service
    if categoria_servicio_id and categoria_servicio_id.isdigit():
        qs = qs.filter(reservaservicios__servicio__categoria_id=int(categoria_servicio_id))
    if servicio_id and servicio_id.isdigit():
        qs = qs.filter(reservaservicios__servicio_id=int(servicio_id))

    # Remove duplicates if joins create duplicates
    qs = qs.distinct()

    # Calculate total in the date range
    total_en_rango = qs.aggregate(total=Sum('total'))['total'] or 0

    # Get categories and services for the filter form
    categorias_servicio = CategoriaServicio.objects.all()
    servicios = Servicio.objects.all()

    context = {
        'venta_reservas': qs,
        'categorias_servicio': categorias_servicio,
        'servicios': servicios,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'categoria_servicio_id': categoria_servicio_id,
        'servicio_id': servicio_id,
        'total_en_rango': total_en_rango,
    }

    return render(request, 'ventas/venta_reserva_list.html', context)

def venta_reserva_detail(request, pk):
    venta = get_object_or_404(
        VentaReserva.objects.prefetch_related(
            'reservaservicios__servicio',
            'reservaproductos__producto',
            'pagos',
            'cliente',
        ),
        pk=pk,
    )
    
    context = {
        'venta': venta,
    }
    return render(request, 'ventas/venta_reserva_detail.html', context)

@login_required
def servicios_vendidos_view(request):
    servicios = ReservaServicio.objects.select_related('servicio__categoria', 'venta_reserva__cliente').all()

    context = {
        'servicios': servicios,
    }

    return render(request, 'ventas/servicios_vendidos.html', context)

@login_required
def actualizar_estado_servicio(request, servicio_id):
    servicio = get_object_or_404(ReservaServicio, id=servicio_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(ReservaServicio.ESTADO_CHOICES).keys():
            servicio.estado = nuevo_estado
            servicio.save()
            messages.success(request, "Estado actualizado correctamente.")
        else:
            messages.error(request, "Estado inválido.")
    
    return redirect('servicios_vendidos')

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


# Función para verificar si el usuario es administrador
def es_administrador(user):
    return user.is_superuser

@user_passes_test(es_administrador)  # Restringir el acceso a administradores
def auditoria_movimientos_view(request):
    # Obtener los parámetros del filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    cliente_id = request.GET.get('cliente')
    tipo_movimiento = request.GET.get('tipo_movimiento')
    usuario_username = request.GET.get('usuario')  # Cambiar a username en lugar de id

    # Obtener todos los movimientos, pre-cargando datos del cliente y usuario
    movimientos = MovimientoCliente.objects.select_related('cliente', 'usuario').all()

    # Filtrar por cliente si se proporciona
    if cliente_id:
        movimientos = movimientos.filter(cliente_id=cliente_id)

    # Filtrar por rango de fechas si se proporciona
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        movimientos = movimientos.filter(fecha_movimiento__gte=fecha_inicio)
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
        movimientos = movimientos.filter(fecha_movimiento__lte=fecha_fin)

    # Filtrar por tipo de movimiento si se proporciona
    if tipo_movimiento and tipo_movimiento != 'None':
        movimientos = movimientos.filter(tipo_movimiento=tipo_movimiento)

    # Filtrar por usuario si se proporciona
    if usuario_username and usuario_username != 'None':
        movimientos = movimientos.filter(usuario__username=usuario_username)

    # Obtener todos los usuarios para la lista desplegable
    usuarios = User.objects.all()

    # Pasar los movimientos al contexto de la plantilla
    context = {
        'movimientos': movimientos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'cliente_id': cliente_id,
        'tipo_movimiento': tipo_movimiento if tipo_movimiento != 'None' else '',
        'usuario_username': usuario_username if usuario_username != 'None' else '',
        'usuarios': usuarios,  # Enviar los usuarios al contexto para la lista desplegable
    }

    return render(request, 'ventas/auditoria_movimientos.html', context)

@user_passes_test(es_administrador)  # Restringir el acceso a administradores
def caja_diaria_view(request):
    # Obtener rango de fechas desde los parámetros GET
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    metodo_pago = request.GET.get('metodo_pago')
    usuario_id = request.GET.get('usuario')

    today = timezone.localdate()
    if not fecha_inicio:
        fecha_inicio = today.strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = today.strftime('%Y-%m-%d')

    fecha_inicio_parsed = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin_parsed = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
    fecha_fin_parsed_datetime = timezone.make_aware(fecha_fin_parsed)

    pagos = Pago.objects.filter(
        fecha_pago__range=(fecha_inicio, fecha_fin_parsed_datetime)
    )

    if usuario_id and usuario_id.isdigit():
        pagos = pagos.filter(usuario__id=usuario_id)

    if metodo_pago:
        pagos = pagos.filter(metodo_pago=metodo_pago)

    ventas = VentaReserva.objects.filter(
        pagos__in=pagos
    ).distinct()

    total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0
    total_pagos = pagos.aggregate(total=Sum('monto'))['total'] or 0

    pagos_grouped = pagos.values('metodo_pago', 'usuario__username').annotate(
        total_monto=Sum('monto'),
        cantidad_transacciones=Count('id')
    ).order_by('metodo_pago', 'usuario__username')

    usuarios = User.objects.filter(is_staff=True)  # Filtrar solo usuarios staff si aplica

    context = {
        'ventas': ventas,
        'pagos': pagos,
        'total_ventas': total_ventas,
        'total_pagos': total_pagos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'pagos_grouped': pagos_grouped,
        'usuarios': usuarios,
        'usuario_id': int(usuario_id) if usuario_id and usuario_id.isdigit() else '',
        'metodo_pago': metodo_pago or '',
        'METODOS_PAGO': Pago.METODOS_PAGO,
    }

    return render(request, 'ventas/caja_diaria.html', context)

def caja_diaria_recepcionistas_view(request):
    # Lista de usuarios permitidos (por username)
    usuarios_permitidos_usernames = ['Lina', 'Edson', 'Ernesto', 'Rafael']
    usuarios_permitidos = User.objects.filter(username__in=usuarios_permitidos_usernames)

    # Obtener rango de fechas y filtros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    metodo_pago = request.GET.get('metodo_pago')
    usuario_id = request.GET.get('usuario')

    # Establecer fechas por defecto
    today = timezone.localdate()
    if not fecha_inicio:
        fecha_inicio = today.strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = today.strftime('%Y-%m-%d')

    # Parsear fechas
    try:
        fecha_inicio_parsed = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_parsed = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    except ValueError:
        fecha_inicio_parsed = today
        fecha_fin_parsed = today

    # Validar fechas
    if fecha_inicio_parsed > fecha_fin_parsed:
        fecha_inicio_parsed, fecha_fin_parsed = fecha_fin_parsed, fecha_inicio_parsed
        fecha_inicio, fecha_fin = fecha_fin, fecha_inicio

    # Ajustar fecha_fin
    fecha_fin_parsed_datetime = timezone.make_aware(datetime.combine(fecha_fin_parsed, datetime.max.time()))

    # Filtrar pagos
    pagos = Pago.objects.filter(
        fecha_pago__range=(fecha_inicio_parsed, fecha_fin_parsed_datetime),
        usuario__in=usuarios_permitidos
    )

    if usuario_id and usuario_id.isdigit():
        pagos = pagos.filter(usuario__id=usuario_id)

    if metodo_pago:
        pagos = pagos.filter(metodo_pago=metodo_pago)

    # Filtrar ventas basadas en pagos filtrados
    ventas = VentaReserva.objects.filter(
        pagos__in=pagos
    ).distinct()

    # Calcular totales
    total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0
    total_pagos = pagos.aggregate(total=Sum('monto'))['total'] or 0

    # Agrupar pagos
    pagos_grouped = pagos.values('metodo_pago').annotate(
        total_monto=Sum('monto'),
        cantidad_transacciones=Count('id')
    ).order_by('metodo_pago')

    # Contexto
    context = {
        'ventas': ventas,
        'pagos': pagos,
        'total_ventas': total_ventas,
        'total_pagos': total_pagos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'pagos_grouped': pagos_grouped,
        'usuarios': usuarios_permitidos,
        'usuario_id': usuario_id or '',
        'metodo_pago': metodo_pago or '',
        'METODOS_PAGO': Pago.METODOS_PAGO,
    }

    return render(request, 'ventas/caja_diaria_recepcionistas.html', context)

@login_required
def crear_venta_reserva_view(request):
    if request.method == 'POST':
        form = VentaReservaForm(request.POST)
        if form.is_valid():
            venta_reserva = form.save()
            messages.success(request, "Venta/Reserva creada correctamente.")
            return redirect('venta_reserva_detail', pk=venta_reserva.pk)
    else:
        form = VentaReservaForm()

    context = {
        'form': form,
    }

    return render(request, 'ventas/crear_venta_reserva.html', context)