FROM python:3.11-slim

WORKDIR /app

# 1) copy only requirements first for better caching
COPY requirements.txt .

# 2) install deps
RUN pip install --no-cache-dir -r requirements.txt

# 3) now copy the rest of the source
COPY . .

CMD ["python", "main.py"]