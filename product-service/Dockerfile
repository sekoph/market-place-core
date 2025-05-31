# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Python dependencies
WORKDIR /app/product-service


# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY product-service/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY  shared/ /app/shared/

# Copy ONLY necessary files
COPY product-service/ /app/product-service/



# Run your application
# CMD python manage.py runserver 0.0.0.0:8001
CMD ["python", "manage.py", "runserver", "0.0.0.0:8003"]
