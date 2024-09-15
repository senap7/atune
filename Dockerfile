# Dockerfile
FROM python:3.9.19-bookworm

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True
ENV APP_HOME /back-end
WORKDIR $APP_HOME
COPY . ./

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app