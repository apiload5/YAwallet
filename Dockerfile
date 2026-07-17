FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend folder contents to /app
COPY backend/ /app/

# Copy root files
COPY manage.py /app/
COPY gunicorn.conf.py /app/
COPY entrypoint.sh /app/

RUN mkdir -p /app/logs /app/staticfiles /app/media

# Set Python path
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=yawallet.settings
ENV PYTHONUNBUFFERED=1

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--config", "gunicorn.conf.py", "yawallet.wsgi:application"]
