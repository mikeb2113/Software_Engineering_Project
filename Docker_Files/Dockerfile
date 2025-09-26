FROM python:3.11-slim

WORKDIR /app

<<<<<<< HEAD
# 1) copy only requirements first for better caching
COPY requirements.txt .

# 2) install deps
RUN pip install --no-cache-dir -r requirements.txt

# 3) now copy the rest of the source
COPY . .

CMD ["python", "main.py"]
=======
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
>>>>>>> 033e36a (Add .gitattributes and normalize line endings)
