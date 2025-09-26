FROM python:3.11-slim

WORKDIR /app

# copy reqs first for caching
COPY Docker_Files/requirements.txt /app/requirements.txt

# optional: curl for your healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# install deps
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy the rest of your project (build context = repo root)
COPY . /app

EXPOSE 8000
CMD ["python", "app.py"]
