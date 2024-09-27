#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

# Función para extraer DB_HOST y DB_PORT de DATABASE_URL usando Python
extract_db_host_port() {
    # Usar Python para parsear DATABASE_URL y extraer host y port
    eval "$(python -c "import os
from urllib.parse import urlparse

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print('Error: DATABASE_URL no está definido.')
    exit(1)

parsed_url = urlparse(database_url)

db_host = parsed_url.hostname
db_port = parsed_url.port if parsed_url.port else 5432  # Puerto predeterminado de PostgreSQL

if not db_host or not db_port:
    print('Error: No se pudo extraer DB_HOST y DB_PORT de DATABASE_URL.')
    exit(1)

print(f'DB_HOST={db_host}')
print(f'DB_PORT={db_port}')
")"

    # Verificar que DB_HOST y DB_PORT fueron extraídos correctamente
    if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ]; then
        echo "Error: No se pudo extraer DB_HOST y DB_PORT de DATABASE_URL."
        exit 1
    fi
}

# Extraer DB_HOST y DB_PORT
extract_db_host_port

# Debugging: Imprimir DB_HOST y DB_PORT (Eliminar en producción)
echo "DATABASE_URL: $DATABASE_URL"
echo "DB_HOST: $DB_HOST"
echo "DB_PORT: $DB_PORT"

# Esperar a que la base de datos esté disponible
echo "Esperando a que la base de datos esté disponible en $DB_HOST:$DB_PORT..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "Base de datos está disponible."

# Aplicar migraciones de Django
echo "Aplicando migraciones..."
python manage.py migrate

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar Gunicorn para servir la aplicación
echo "Iniciando Gunicorn en el puerto $PORT..."
exec gunicorn aremko_project.wsgi:application --bind 0.0.0.0:"$PORT"
