from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import timedelta
from django.conf import settings
import os

def crear_evento_calendar(reserva):
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'credenciales.json')

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)

    evento = {
        'summary': f"Reserva de {reserva.producto.nombre}",
        'description': f"Cliente: {reserva.cliente}",
        'start': {
            'dateTime': reserva.fecha_reserva.isoformat(),
            'timeZone': settings.TIME_ZONE,
        },
        'end': {
            'dateTime': (reserva.fecha_reserva + reserva.producto.duracion_reserva).isoformat(),
            'timeZone': settings.TIME_ZONE,
        },
    }

    evento_creado = service.events().insert(calendarId='tu_calendar_id', body=evento).execute()
    return evento_creado.get('id')
