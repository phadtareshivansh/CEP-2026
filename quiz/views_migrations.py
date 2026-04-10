"""
Vercel API endpoint to trigger migrations on-demand
Run this once after deployment to initialize the database
"""

import os
import json
from django.core.management import call_command
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def trigger_migrations(request):
    """
    POST /api/migrations/ to run Django migrations
    This is a simple endpoint to initialize the database on Vercel
    """
    
    # Simple security check - require a token if in production
    if not os.environ.get('DEBUG', 'True').lower() == 'true':
        token = request.POST.get('token') or request.headers.get('X-Migration-Token')
        expected_token = os.environ.get('MIGRATION_TOKEN')
        
        if not expected_token or token != expected_token:
            return JsonResponse({
                'error': 'Unauthorized'
            }, status=401)
    
    try:
        # Run migrations
        call_command('migrate', '--noinput', verbosity=2)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Migrations completed successfully'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
