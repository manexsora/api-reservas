FROM python:3.11-slim

# PYTHONDONTWRITEBYTECODE = evita la creación de archivos .pyc
# PYTHONUNBUFFERED = asegura que los logs de Python sean visibles inmediatamente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DB_PATH=/app/db/database.db
ENV PYTHONPATH="/app" 

# Todas las operaciones siguientes se ejecutarán desde /app
WORKDIR /app

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata cron \
    && echo "Europe/Madrid" > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalar dependencias.
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Copiar crontab vacío inicial
RUN touch /etc/crontab

# Redirigir logs de cron a stdout
RUN ln -sf /dev/stdout /var/log/cron_custom.log

# Ejecutar cron + uvicorn simultáneamente
CMD cron && uvicorn main:app --host 0.0.0.0 --port 8080