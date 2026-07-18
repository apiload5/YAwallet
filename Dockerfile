# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=settings \
    PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy render build script (optional, for Render)
COPY render-build.sh /render-build.sh
RUN chmod +x /render-build.sh

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media

# Use entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Start command
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8000"]
