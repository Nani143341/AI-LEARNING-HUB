# Use the official Python slim image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app/

# Expose the port for the application
EXPOSE 8080

# Run the web server
CMD ["gunicorn", "--bind", ":$PORT", "--workers", "2", "--threads", "4", "myapp.wsgi"]
