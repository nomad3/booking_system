# Usa la imagen oficial de Python como base
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requisitos
COPY requirements.txt /app/

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación
COPY . /app/

# Exponer el puerto
EXPOSE 8000

# Comando por defecto
CMD ["gunicorn", "aremko_project.wsgi:application", "--bind", "0.0.0.0:8000"]
