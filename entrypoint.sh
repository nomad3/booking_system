#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

# Función para esperar a que la base de datos esté disponible
wait_for_db() {
  echo "Esperando a que la base de datos esté disponible en $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 0.1
  done
  echo "Base de datos está disponible."
}

# Llamar a la función para esperar a la base de datos
wait_for_db

# Aplicar migraciones de Django
echo "Aplicando migraciones..."
python manage.py migrate

# Iniciar Gunicorn para servir la aplicación
echo "Iniciando Gunicorn en el puerto $PORT..."
exec gunicorn aremko_project.wsgi:application --bind 0.0.0.0:"$PORT"
