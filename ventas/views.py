from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Proveedor, CategoriaProducto, Producto, Reserva, Venta
from .serializers import (
    ProveedorSerializer,
    CategoriaProductoSerializer,
    ProductoSerializer,
    ReservaSerializer,
    VentaSerializer
)
import openai
import os

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

@api_view(['POST'])
def manychat_webhook(request):
    data = request.data
    cliente = data.get('cliente')
    producto_id = data.get('producto_id')
    cantidad = int(data.get('cantidad', 1))
    fecha_reserva = data.get('fecha_reserva')  # Formato ISO 8601

    try:
        producto = Producto.objects.get(id=producto_id)
        if producto.cantidad_disponible < cantidad:
            return Response({'status': 'error', 'message': 'Cantidad no disponible'}, status=400)
        if producto.es_reservable:
            reserva = Reserva.objects.create(
                producto=producto,
                cliente=cliente,
                cantidad=cantidad,
                fecha_reserva=fecha_reserva
            )
            return Response({'status': 'success', 'reserva_id': reserva.id})
        else:
            venta = Venta.objects.create(
                producto=producto,
                cliente=cliente,
                cantidad=cantidad
            )
            return Response({'status': 'success', 'venta_id': venta.id})
    except Producto.DoesNotExist:
        return Response({'status': 'error', 'message': 'Producto no encontrado'}, status=404)

@csrf_exempt
@api_view(['POST'])
def manychat_chatgpt_webhook(request):
    data = request.data
    user_message = data.get('text', '')
    user_id = data.get('user_id')

    # Configurar la API Key de OpenAI
    openai.api_key = os.environ.get('OPENAI_API_KEY')

    try:
        # Generar respuesta con ChatGPT
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"Cliente: {user_message}\nAsistente:",
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.9,
        )

        chatgpt_reply = response.choices[0].text.strip()

        # Añadir lógica para procesar reservas
        if 'reservar' in user_message.lower():
            # Intentar extraer información relevante usando ChatGPT
            extraction_prompt = (
                f"Extrae la siguiente información del mensaje del cliente y devuélvela en formato JSON:\n"
                f"Mensaje: \"{user_message}\"\n"
                f"Información requerida: fecha_reserva, tipo_servicio, cantidad\n"
                f"Si falta algún dato, usa null.\n\n"
                f"Respuesta en JSON:"
            )
            extraction_response = openai.Completion.create(
                engine='text-davinci-003',
                prompt=extraction_prompt,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0,
            )
            extracted_info = extraction_response.choices[0].text.strip()

            import json
            try:
                info = json.loads(extracted_info)
                # Validar que tenemos la información necesaria
                if info.get('fecha_reserva') and info.get('tipo_servicio') and info.get('cantidad'):
                    # Buscar el producto
                    producto = Producto.objects.filter(nombre__icontains=info['tipo_servicio']).first()
                    if producto:
                        # Crear la reserva
                        reserva = Reserva.objects.create(
                            producto=producto,
                            cliente=user_id,  # Aquí podrías mapear el user_id a un cliente real
                            cantidad=int(info['cantidad']),
                            fecha_reserva=info['fecha_reserva']
                        )
                        chatgpt_reply += f"\n\n¡Reserva realizada con éxito para {producto.nombre} el {info['fecha_reserva']}!"
                    else:
                        chatgpt_reply += "\n\nLo siento, no pude encontrar el servicio que solicitaste."
                else:
                    chatgpt_reply += "\n\nPor favor, proporciona más detalles para realizar la reserva."
            except json.JSONDecodeError:
                chatgpt_reply += "\n\nNo pude entender tu solicitud de reserva. ¿Podrías proporcionar más detalles?"

        # Devolver respuesta a ManyChat
        return Response({
            'messages': [
                {'text': chatgpt_reply}
            ]
        })
    except Exception as e:
        # Manejo de errores
        return Response({
            'messages': [
                {'text': "Lo siento, hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde."}
            ]
        }, status=500)
