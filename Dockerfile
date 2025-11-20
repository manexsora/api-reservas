FROM python:3.11-slim

# PYTHONDONTWRITEBYTECODE = evita la creación de archivos .pyc
# PYTHONUNBUFFERED = asegura que los logs de Python sean visibles inmediatamente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DB_PATH=/app/db/database.db
ENV PYTHONPATH="/app" 

# Todas las operaciones siguientes se ejecutarán desde /app
WORKDIR /app

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalar dependencias.
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Copiar crontab vacío inicial
RUN touch /etc/crontab

# Ejecutar cron + uvicorn simultáneamente
CMD cron && uvicorn main:app --host 0.0.0.0 --port 8000