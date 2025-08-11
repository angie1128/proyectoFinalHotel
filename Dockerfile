# Usar Python 3.13.5 como imagen base
FROM python:3.13.5-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio para uploads
RUN mkdir -p uploads

# Exponer el puerto 5000
EXPOSE 8086

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Comando para ejecutar la aplicación (usa variables de entorno para la base de datos)
CMD ["sh", "-c", "flask run --host=0.0.0.0 --port=8086"]