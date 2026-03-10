FROM python:3.11-slim

# Evita archivos basura de python y fuerza salida por consola
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# Instalamos dependencias del sistema necesarias para compilar psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instalamos las librerías
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiamos el código
COPY . /code/

# Crear carpeta de static para evitar el UserWarning de WhiteNoise
RUN mkdir -p /code/staticfiles

# Comando sugerido para el Dockerfile con manejo de concurrencia
CMD gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --threads 2 --timeout 60
