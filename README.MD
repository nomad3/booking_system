README.md
Proyecto Aremko Booking System
Este es un sistema de reservas y ventas para Aremko, construido con Django y Docker. Incluye funcionalidades para manejar pagos parciales y distintos métodos de pago.

Tabla de Contenidos
Requisitos Previos
Configuración en Ambiente Local
1. Clonar el Repositorio
2. Configurar Variables de Entorno
3. Construir y Levantar los Contenedores
4. Aplicar Migraciones y Crear Superusuario
5. Acceder a la Aplicación
Configuración en Ambiente de Producción
1. Configurar Servidor
2. Configurar Variables de Entorno para Producción
3. Construir y Levantar los Contenedores en Modo Producción
4. Configurar Servidor Web (Opcional)
Variables de Entorno
Comandos Útiles
Notas Adicionales
Requisitos Previos
Docker y Docker Compose instalados en el sistema.
Git para clonar el repositorio.
Opcional: Conocimientos básicos de Python y Django.
Configuración en Ambiente Local
1. Clonar el Repositorio
Clona el repositorio del proyecto a tu máquina local:

bash
Copiar código
git clone https://github.com/tu_usuario/aremko_booking_system.git
cd aremko_booking_system
2. Configurar Variables de Entorno
Crea un archivo .env en el directorio raíz del proyecto:

bash
Copiar código
touch .env
Agrega las siguientes variables al archivo .env:

env
Copiar código
# Variables de Django
SECRET_KEY=tu_clave_secreta
DEBUG=True

# Configuración de PostgreSQL
POSTGRES_DB=aremko_db
POSTGRES_USER=aremko_user
POSTGRES_PASSWORD=aremko_password
DB_HOST=db
DB_PORT=5432

# API Key de OpenAI (si aplica)
OPENAI_API_KEY=tu_api_key_de_openai

# Otros
ALLOWED_HOSTS=*
3. Construir y Levantar los Contenedores
Ejecuta el siguiente comando para construir las imágenes y levantar los contenedores:

bash
Copiar código
docker compose up --build
4. Aplicar Migraciones y Crear Superusuario
En otra terminal, aplica las migraciones:

bash
Copiar código
docker compose exec web python manage.py migrate
Crea un superusuario para acceder al panel de administración:

bash
Copiar código
docker compose exec web python manage.py createsuperuser
Sigue las instrucciones para establecer el nombre de usuario y la contraseña.

5. Acceder a la Aplicación
Aplicación Web: Visita http://localhost:8000/ en tu navegador.
Panel de Administración: Visita http://localhost:8000/admin/ e inicia sesión con el superusuario.
Configuración en Ambiente de Producción
1. Configurar Servidor
Sistema Operativo: Se recomienda un servidor con Linux (Ubuntu, Debian, etc.).
Instalar Docker y Docker Compose:
bash
Copiar código
sudo apt update
sudo apt install docker.io docker-compose
2. Configurar Variables de Entorno para Producción
En el servidor, crea un archivo .env con las variables adecuadas:

env
Copiar código
# Variables de Django
SECRET_KEY=una_clave_secreta_segura
DEBUG=False

# Configuración de PostgreSQL
POSTGRES_DB=aremko_db
POSTGRES_USER=aremko_user
POSTGRES_PASSWORD=aremko_password_segura
DB_HOST=db
DB_PORT=5432

# API Key de OpenAI (si aplica)
OPENAI_API_KEY=tu_api_key_de_openai

# Otros
ALLOWED_HOSTS=tu_dominio.com
3. Construir y Levantar los Contenedores en Modo Producción
En producción, es recomendable utilizar un servidor de aplicaciones como Gunicorn y un servidor web como Nginx.

Actualizar Dockerfile para Producción
Modifica el Dockerfile para utilizar Gunicorn:

dockerfile
Copiar código
# Usar una imagen base ligera
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto de Gunicorn
EXPOSE 8000

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "aremko_project.wsgi:application"]
Levantar los Contenedores
bash
Copiar código
docker compose up --build -d
4. Configurar Servidor Web (Opcional)
Para servir la aplicación en el puerto 80 o 443, puedes utilizar Nginx como proxy inverso.

Instalar Nginx
bash
Copiar código
sudo apt install nginx
Configurar Nginx
Crea un archivo de configuración para tu sitio en /etc/nginx/sites-available/aremko:

nginx
Copiar código
server {
    listen 80;
    server_name tu_dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
Habilita el sitio y reinicia Nginx:

bash
Copiar código
sudo ln -s /etc/nginx/sites-available/aremko /etc/nginx/sites-enabled/
sudo systemctl restart nginx
Variables de Entorno
SECRET_KEY: Clave secreta de Django. Debe ser segura y no compartirse.
DEBUG: Establecer en False en producción.
POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD: Credenciales de la base de datos.
DB_HOST, DB_PORT: Configuración de conexión a la base de datos.
OPENAI_API_KEY: Clave de API para OpenAI, si es utilizada.
ALLOWED_HOSTS: Lista de dominios o direcciones IP permitidas.
Comandos Útiles
Aplicar migraciones:

bash
Copiar código
docker compose exec web python manage.py migrate
Crear superusuario:

bash
Copiar código
docker compose exec web python manage.py createsuperuser
Ver logs de los contenedores:

bash
Copiar código
docker compose logs -f
Detener contenedores:

bash
Copiar código
docker compose down
Notas Adicionales
Seguridad:

Asegúrate de no subir el archivo .env al repositorio.
En producción, utiliza HTTPS configurando certificados SSL con Let's Encrypt.
Persistencia de Datos:

Los datos de la base de datos se almacenan en un volumen Docker llamado postgres_data.
Asegúrate de realizar backups periódicos de la base de datos.
Actualizaciones:

Cuando realices cambios en el código o dependencias, reconstruye las imágenes y reinicia los contenedores:

bash
Copiar código
docker compose build
docker compose up -d
