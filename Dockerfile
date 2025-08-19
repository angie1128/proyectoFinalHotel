FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p migrations

# El contenedor expone 8086
EXPOSE 8086

# Gunicorn escuchando en 8086 (el puerto interno)
CMD ["gunicorn", "-b", "0.0.0.0:8086", "run:app"]
