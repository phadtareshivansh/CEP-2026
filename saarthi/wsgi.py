"""
WSGI config for saarthi project.
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saarthi.settings')

# Get the Django WSGI application
django_application = get_wsgi_application()

# Flag to track if migrations have been attempted
_migrations_attempted = False


def run_migrations():
    """Attempt to run Django migrations. Safe to call multiple times."""
    global _migrations_attempted
    
    if _migrations_attempted:
        return
    
    _migrations_attempted = True
    
    try:
        from django.core.management import call_command
        call_command('migrate', '--noinput', verbosity=0)
    except Exception as e:
        # Log but don't fail - database might not be ready yet
        print(f"Warning: Could not run migrations: {str(e)}", file=sys.stderr)


class VercelWsgiWrapper:
    """
    WSGI middleware to handle Vercel's forwarded headers and allow any *.vercel.app domain.
    This runs BEFORE Django's host validation, so it can properly set HTTP_HOST.
    """
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Run migrations on first request (if in production)
        if not os.environ.get('DEBUG', 'True').lower() == 'true':
            run_migrations()
        
        host = environ.get('HTTP_HOST', '')
        
        # If on Vercel and host ends with .vercel.app, it's valid
        # Add it to ALLOWED_HOSTS dynamically
        if host.endswith('.vercel.app'):
            from django.conf import settings
            if host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(host)
        
        # Also handle X_FORWARDED_HOST header from Vercel
        x_forwarded_host = environ.get('HTTP_X_FORWARDED_HOST', '')
        if x_forwarded_host and x_forwarded_host.endswith('.vercel.app'):
            if x_forwarded_host not in settings.ALLOWED_HOSTS:
                from django.conf import settings
                settings.ALLOWED_HOSTS.append(x_forwarded_host)
        
        return self.app(environ, start_response)


# Wrap Django application with Vercel WSGI middleware
application = VercelWsgiWrapper(django_application)

# Vercel serverless function entry point
app = application


