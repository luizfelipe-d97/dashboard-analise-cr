FROM python:3.9-slim

WORKDIR /app

# Instala dependências essenciais
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libgomp1 && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /tmp/uploads && \
    chmod 777 /tmp/uploads

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--workers", "2", "--timeout", "300", "--preload"]