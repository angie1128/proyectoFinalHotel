# Imagen base estable
FROM python:3.11-slim

# Evita buffering en logs de Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (para compilar algunas librerías de Python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (mejora la cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Crear carpeta de migraciones si no existe
RUN mkdir -p migrations

# Exponer puerto interno
EXPOSE 8086

# Comando de arranque con Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8086", "run:app"]
