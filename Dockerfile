# Use the official Python image.
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

# Copy application dependency manifests to the container image.
COPY requirements.txt ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /apps
WORKDIR $APP_HOME
COPY . .

# Ensure the static files directory is writable
RUN mkdir -p /apps/static/files && chmod -R 755 /apps/static/files

# Expose the default port for Cloud Run
EXPOSE 8080

# Run the web service on container startup
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 myapp.wsgi"]

RUN python manage.py create_admin