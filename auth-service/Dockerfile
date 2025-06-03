# # Dockerfile
# FROM python:3.11-slim

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Install Python dependencies
# WORKDIR /app
# COPY requirements.txt /app/requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy ONLY necessary files
# COPY . /app

# # Run your application
# CMD python manage.py runserver 0.0.0.0:8000


# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Install Python dependencies
WORKDIR /app/auth-service


# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY auth-service/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY  shared/ /app/shared/

# Copy ONLY necessary files
COPY auth-service/ /app/auth-service/



# Run your application
# CMD python manage.py runserver 0.0.0.0:8001
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
