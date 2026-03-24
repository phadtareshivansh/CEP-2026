from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse
from datetime import timedelta
import json


class SessionTimeoutMiddleware:
    """
    ERP-style session timeout middleware.
    Logs out user if session is idle for more than SESSION_COOKIE_AGE.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # List of paths that don't require authentication
        public_paths = [
            reverse('quiz:index'),
            reverse('quiz:login'),
            reverse('quiz:signup'),
            '/api/login/',
            '/api/signup/',
            '/static/',
        ]
        
        # Check if user is authenticated and session exists
        if request.user.is_authenticated:
            last_activity = request.session.get('_last_activity')
            now = timezone.now()
            
            if last_activity:
                # Convert string to datetime if needed
                if isinstance(last_activity, str):
                    last_activity = timezone.datetime.fromisoformat(last_activity)
                
                # Session timeout check (30 minutes)
                timeout_duration = timedelta(minutes=30)
                if now - last_activity > timeout_duration:
                    # Session has expired - logout user
                    from django.contrib.auth import logout
                    logout(request)
                    
                    # Redirect to login with message
                    if request.path not in public_paths:
                        return redirect(f"{reverse('quiz:login')}?session_expired=true")
            
            # Update last activity timestamp
            request.session['_last_activity'] = now.isoformat()
        
        response = self.get_response(request)
        return response
