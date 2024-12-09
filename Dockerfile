FROM python:3.9-slim

ENV PYTHONUNBUFFERED True

COPY requirements.txt ./
RUN pip install -r requirements.txt

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 myapp.wsgi && python manage.py migrate && python manage.py shell < create_superuser.py
