"""
WSGI config for yawallet project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, '/app')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yawallet.settings')

application = get_wsgi_application()
