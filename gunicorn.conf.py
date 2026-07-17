import multiprocessing
import os
import sys

# Add /app to Python path
sys.path.insert(0, '/app')

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"
preload_app = True
worker_class = "sync"

# Correct WSGI path - yawallet is in /app/
raw_env = [
    f"DJANGO_SETTINGS_MODULE=yawallet.settings",
]
