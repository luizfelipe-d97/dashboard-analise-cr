FROM python:3.9-slim

WORKDIR /app

# Instala dependências para processamento de Excel
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libgomp1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY . .

# Aumenta timeout e workers
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--workers", "4", "--timeout", "300", "--preload"]

# Adicione esta linha para instalar dependências do sistema
RUN apt-get update && apt-get install -y python3-dev libgomp1 && rm -rf /var/lib/apt/lists/*