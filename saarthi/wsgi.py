"""
WSGI config for saarthi project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saarthi.settings')

application = get_wsgi_application()

# Vercel serverless function entry point
app = application
