# Dockerfile

# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y build-essential libpq-dev netcat && rm -rf /var/lib/apt/lists/*

# Copiar los archivos de requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Copiar el script de entrada
COPY entrypoint.sh /entrypoint.sh

# Dar permisos de ejecución al script de entrada
RUN chmod +x /entrypoint.sh

# Exponer el puerto que usará la aplicación (Render asigna el puerto via variable de entorno PORT)
EXPOSE 8000

# Establecer el script de entrada como el punto de entrada
ENTRYPOINT ["/entrypoint.sh"]
