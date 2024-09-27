#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

# Función para extraer el host y el puerto de DATABASE_URL
extract_db_host_port() {
    # DATABASE_URL tiene el formato: postgres://user:password@host:port/dbname
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\(.*\):\(.*\)/.*|\1|p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's|.*@.*:\(.*\)/.*|\1|p')
    
    if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ]; then
        echo "Error: No se pudo extraer DB_HOST y DB_PORT de DATABASE_URL."
        exit 1
    fi
}

# Extraer DB_HOST y DB_PORT
extract_db_host_port

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
