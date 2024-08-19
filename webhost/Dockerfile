# Use the official Python image as a base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOCKER_BUILDKIT=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN openssl req \
-x509 \
-out cert.pem \
-keyout key.pem \
-newkey rsa:4096 \
-days 365 \
-nodes \
-sha256 \
-subj "/C=US/ST=NY/L=NY/O=ACME/OU=CD/CN=AcmeWPDeveloper"

# Copy the application code
COPY ./* /app/
RUN touch /app/app.db
RUN touch /app/webhost.log
RUN touch /app/deep_learning_server.log

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]
