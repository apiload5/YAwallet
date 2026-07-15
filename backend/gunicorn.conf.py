import multiprocessing
import os

# Bind to port
bind = "0.0.0.0:8000"

# Number of workers
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Timeout
timeout = 120

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Preload application
preload_app = True

# Graceful timeout
graceful_timeout = 30

# Keep alive
keepalive = 5

# Environment variables
raw_env = [
    f"DJANGO_SETTINGS_MODULE={os.environ.get('DJANGO_SETTINGS_MODULE', 'yawallet.settings')}",
]
