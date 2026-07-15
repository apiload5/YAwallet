# Use Python 3.12
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies (INCLUDING netcat)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    netcat-openbsd \      # ← YEH ADD KARO
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/staticfiles /app/media

# Set environment variables
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=yawallet.settings
ENV PYTHONUNBUFFERED=1

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 8000

# Run entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--config", "gunicorn.conf.py", "yawallet.wsgi:application"]
