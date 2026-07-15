# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Create directories and user BEFORE copying code
RUN mkdir -p /app/logs /app/staticfiles /app/media && \
    adduser --disabled-password --gecos '' django && \
    chown -R django:django /app

# Copy project files with correct ownership
COPY --chown=django:django . .

# Set environment variables
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=yawallet.settings
ENV PYTHONUNBUFFERED=1

# Copy and setup entrypoint
COPY --chown=django:django entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user
USER django

# Health check (uncomment when /health/ endpoint exists)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
#     CMD curl -f http://localhost:8000/health/ || exit 1

# Entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["gunicorn", "--config", "gunicorn.conf.py", "yawallet.wsgi:application"]
