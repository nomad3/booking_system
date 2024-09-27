# Dockerfile

# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copiar los archivos de requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto que usará la aplicación (Render asigna el puerto via variable de entorno PORT)
EXPOSE 8000

# Comando para iniciar la aplicación usando Gunicorn, escuchando en el puerto especificado por Render
CMD gunicorn booking_system.wsgi:application --bind 0.0.0.0:${PORT}
