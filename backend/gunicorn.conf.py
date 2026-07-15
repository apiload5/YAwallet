import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
graceful_timeout = 30
keepalive = 5

# User and group (use if running as root, otherwise comment out)
# user = "django"
# group = "django"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "yawallet"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment when using HTTPS)
# keyfile = "/etc/nginx/ssl/yawallet.key"
# certfile = "/etc/nginx/ssl/yawallet.crt"

# Preload app
preload_app = True

# Environment
raw_env = [
    f"DJANGO_SETTINGS_MODULE={os.environ.get('DJANGO_SETTINGS_MODULE', 'yawallet.settings')}",
]
