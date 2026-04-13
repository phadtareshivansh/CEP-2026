"""
WSGI config for saarthi project.
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saarthi.settings')

# Get the Django WSGI application
django_application = get_wsgi_application()


class ApplicationWrapper:
    """
    WSGI wrapper to handle:
    1. Running migrations on first request (for Vercel where env vars aren't available during build)
    2. Vercel forwarded headers and *.vercel.app domain compatibility
    """
    
    def __init__(self, app):
        self.app = app
        self._migrations_done = False
    
    def __call__(self, environ, start_response):
        # Run migrations once on first request
        if not self._migrations_done:
            try:
                from django.core.management import execute_from_command_line
                execute_from_command_line(['manage.py', 'migrate', '--noinput'])
                self._migrations_done = True
            except Exception as e:
                print(f"Migration at startup failed: {e}", file=sys.stderr)
        
        # Handle Vercel's forwarded headers
        host = environ.get('HTTP_HOST', '')
        if host.endswith('.vercel.app'):
            from django.conf import settings
            if host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(host)
        
        x_forwarded_host = environ.get('HTTP_X_FORWARDED_HOST', '')
        if x_forwarded_host and x_forwarded_host.endswith('.vercel.app'):
            from django.conf import settings
            if x_forwarded_host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(x_forwarded_host)
        
        return self.app(environ, start_response)


# Wrap Django application with our multi-purpose wrapper
application = ApplicationWrapper(django_application)

# Vercel serverless function entry point
app = application
