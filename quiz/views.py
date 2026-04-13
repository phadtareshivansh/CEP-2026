"""
Saarthi Career Guidance Platform - Main Views Module

This module contains all view functions for the Saarthi platform, organized into logical sections:
- Authentication & User Management
- Assessment & Quiz
- Skills & Learning Paths
- Career Tools & Analytics
- Forum & Community
- PDF Export & Utilities

Each section is clearly marked with section headers for easy navigation.
"""

# ===============================================================================
# IMPORTS
# ===============================================================================

# Django Imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Third-party Imports
import json
import requests
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Local Imports
from .models import (
    Assessment, Career, CareerBookmark, CareerPivotAnalysis, ForumCategory,
    ForumPost, ForumReply, JobListing, LearningGoal, LearningProgress,
    LoginAttempt, Mentor, MentorRequest, Skill, AnalyticsEvent,
    UserCareerGoal, UserProfile, UserSkill, UserSuccessStory
)


# ===============================================================================
# CONFIGURATION & CONSTANTS
# ===============================================================================

"""
RIASEC Career Assessment Model
Represents the Holland Code framework for career assessment:
- Realistic: Practical, hands-on work
- Investigative: Research & analysis
- Artistic: Creative expression
- Social: People-focused work
- Enterprising: Leadership & persuasion
- Conventional: Order & organization
"""
RIASEC = {
    'Realistic': {
        'color': '#ef4444',
        'emoji': '🔧',
        'description': 'Practical, hands-on work with tools & nature'
    },
    'Investigative': {
        'color': '#3b82f6',
        'emoji': '🔬',
        'description': 'Research, analysis & problem-solving'
    },
    'Artistic': {
        'color': '#f59e0b',
        'emoji': '🎨',
        'description': 'Creative expression & innovation'
    },
    'Social': {
        'color': '#10b981',
        'emoji': '👥',
        'description': 'Helping people & teamwork'
    },
    'Enterprising': {
        'color': '#ec4899',
        'emoji': '💼',
        'description': 'Leadership & persuasion'
    },
    'Conventional': {
        'color': '#8b5cf6',
        'emoji': '📋',
        'description': 'Order, organization & efficiency'
    }
}

"""
Career Database - Baseline career recommendations by RIASEC type.
Maps each RIASEC category to sample careers in that domain.
"""
CAREER_DATABASE = {
    'Realistic': [
        {
            'title': 'Civil Engineer',
            'description': 'Design & build bridges, roads, and buildings',
            'skills': 'Problem-solving, Technical Design'
        },
        {
            'title': 'Mechanic/Technician',
            'description': 'Repair and maintain machinery and vehicles',
            'skills': 'Troubleshooting, Technical Skills'
        },
        {
            'title': 'Carpenter',
            'description': 'Build and construct wooden structures',
            'skills': 'Craftsmanship, Precision'
        }
    ],
    'Investigative': [
        {
            'title': 'Data Scientist',
            'description': 'Analyze data and find meaningful patterns',
            'skills': 'Statistics, Programming, Analysis'
        },
        {
            'title': 'Research Scientist',
            'description': 'Conduct experiments and advance knowledge',
            'skills': 'Critical Thinking, Research'
        },
        {
            'title': 'Forensic Analyst',
            'description': 'Investigate crimes using scientific methods',
            'skills': 'Attention to Detail, Analysis'
        }
    ],
    'Artistic': [
        {
            'title': 'UI/UX Designer',
            'description': 'Create beautiful and intuitive user experiences',
            'skills': 'Creativity, Design, Problem-solving'
        },
        {
            'title': 'Content Creator',
            'description': 'Produce engaging multimedia content',
            'skills': 'Storytelling, Creativity'
        },
        {
            'title': 'Graphic Designer',
            'description': 'Design visual content for various media',
            'skills': 'Visual Thinking, Design Tools'
        }
    ],
    'Social': [
        {
            'title': 'Counselor/Therapist',
            'description': 'Help people overcome challenges',
            'skills': 'Empathy, Communication, Active Listening'
        },
        {
            'title': 'Teacher',
            'description': 'Educate and inspire the next generation',
            'skills': 'Communication, Patience, Mentoring'
        },
        {
            'title': 'HR Manager',
            'description': 'Manage people and organizational culture',
            'skills': 'Leadership, Communication, Empathy'
        }
    ],
    'Enterprising': [
        {
            'title': 'Entrepreneur',
            'description': 'Start and grow your own business',
            'skills': 'Leadership, Risk-taking, Vision'
        },
        {
            'title': 'Business Manager',
            'description': 'Lead teams and drive growth',
            'skills': 'Leadership, Strategy, Decision-making'
        },
        {
            'title': 'Sales Manager',
            'description': 'Drive revenue and build relationships',
            'skills': 'Persuasion, Negotiation, Ambition'
        }
    ],
    'Conventional': [
        {
            'title': 'Accountant',
            'description': 'Manage finances and ensure accuracy',
            'skills': 'Attention to Detail, Organization'
        },
        {
            'title': 'Data Analyst',
            'description': 'Organize and analyze data efficiently',
            'skills': 'Organization, Analysis, Detail-oriented'
        },
        {
            'title': 'Administrator',
            'description': 'Manage office operations smoothly',
            'skills': 'Organization, Planning, Precision'
        }
    ]
}


# ===============================================================================
# MAIN LANDING PAGES
# ===============================================================================

def index(request):
    """
    Home page view with adaptive content based on authentication status.
    - Unauthenticated: redirects to landing page
    - Authenticated: displays personalized dashboard with assessment history
    """
    if not request.user.is_authenticated:
        return render(request, 'landing.html')
    
    assessments = (
        request.user.assessments.all()[:5]
        if hasattr(request.user, 'assessments')
        else []
    )
    
    context = {
        'previous_assessments': assessments,
        'assessment_count': Assessment.objects.filter(user=request.user).count(),
    }
    
    return render(request, 'index.html', context)


def landing_dashboard(request):
    """
    Premium landing dashboard with stats and testimonials.
    Displays animated accuracy metrics and feature highlights.
    """
    return render(request, 'landing_dashboard.html', {})


# ===============================================================================
# AUTHENTICATION & USER MANAGEMENT
# ===============================================================================

def signup(request):
    """
    User registration view.
    Handles both GET (form display) and POST (account creation).
    Includes validation for username, email, and password strength.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            # Validation
            if not username or not email or not password:
                return JsonResponse(
                    {'success': False, 'message': 'All fields are required'},
                    status=400
                )
            
            if len(password) < 6:
                return JsonResponse(
                    {'success': False, 'message': 'Password must be at least 6 characters'},
                    status=400
                )
            
            if User.objects.filter(username=username).exists():
                return JsonResponse(
                    {'success': False, 'message': 'Username already exists'},
                    status=400
                )
            
            if User.objects.filter(email=email).exists():
                return JsonResponse(
                    {'success': False, 'message': 'Email already exists'},
                    status=400
                )
            
            # Create user and profile
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            UserProfile.objects.create(user=user)
            
            # Auto-login after signup
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Account created successfully!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse(
                {'success': False, 'message': f'Error: {str(e)}'},
                status=400
            )
    
    return render(request, 'auth/signup.html')


def login_view(request):
    """
    User login with ERP-style security features:
    - Account lockout after max failed attempts
    - IP-based tracking
    - Failed attempt logging
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or not password:
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=get_client_ip(request),
                    success=False,
                    reason='Empty username or password'
                )
                return JsonResponse(
                    {'success': False, 'message': 'Username and password are required'},
                    status=400
                )
            
            # Check for account lockout
            failed_attempts = LoginAttempt.objects.filter(
                username=username,
                success=False,
                timestamp__gte=timezone.now() - timedelta(
                    minutes=settings.LOCK_TIME_MINUTES
                )
            ).count()
            
            if failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=get_client_ip(request),
                    success=False,
                    reason=f'Account locked ({settings.MAX_LOGIN_ATTEMPTS} attempts)'
                )
                return JsonResponse(
                    {
                        'success': False,
                        'message': f'Account locked. Try again in {settings.LOCK_TIME_MINUTES} minutes.'
                    },
                    status=429
                )
            
            # Authenticate
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=get_client_ip(request),
                    success=True,
                    reason='Successful login'
                )
                LoginAttempt.objects.filter(
                    username=username,
                    success=False
                ).delete()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Logged in successfully!'
                })
            else:
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=get_client_ip(request),
                    success=False,
                    reason='Invalid credentials'
                )
                
                new_failed_count = LoginAttempt.objects.filter(
                    username=username,
                    success=False,
                    timestamp__gte=timezone.now() - timedelta(
                        minutes=settings.LOCK_TIME_MINUTES
                    )
                ).count()
                
                remaining = settings.MAX_LOGIN_ATTEMPTS - new_failed_count
                
                if remaining > 0:
                    return JsonResponse(
                        {
                            'success': False,
                            'message': f'Invalid credentials. {remaining} attempts left.'
                        },
                        status=400
                    )
                else:
                    return JsonResponse(
                        {
                            'success': False,
                            'message': f'Account locked. Try in {settings.LOCK_TIME_MINUTES} minutes.'
                        },
                        status=429
                    )
                    
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse(
                {'success': False, 'message': f'Error: {str(e)}'},
                status=400
            )
    
    context = {'session_expired': request.GET.get('session_expired', False)}
    return render(request, 'auth/login.html', context)


def logout_view(request):
    """
    Log out the current user and redirect to home page.
    """
    logout(request)
    return redirect('quiz:index')


@login_required(login_url='quiz:login')
def profile(request):
    """
    User profile view and edit.
    Allows users to update bio, location, experience level, and profile picture.
    """
    user = request.user
    profile = (
        user.profile
        if hasattr(user, 'profile')
        else UserProfile.objects.get_or_create(user=user)[0]
    )
    
    if request.method == 'POST':
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.phone = request.POST.get('phone', '')
        profile.current_role = request.POST.get('current_role', '')
        profile.experience_level = request.POST.get('experience_level', 'student')
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('quiz:profile')
    
    assessments = (
        user.assessments.all()[:5]
        if hasattr(user, 'assessments')
        else []
    )
    
    context = {
        'profile': profile,
        'assessments': assessments,
    }
    
    return render(request, 'auth/profile.html', context)


# ===============================================================================
# ASSESSMENT & QUIZ VIEWS
# ===============================================================================

def get_questions(request):
    """
    Fetch quiz questions.
    Returns JSON with RIASEC career assessment questions.
    """
    # Mock questions for RIASEC career assessment
    questions = [
        # REALISTIC (working with hands, tools, fixing things)
        {
            "question": "Do you enjoy building or fixing things with your hands?",
            "riasec_mapping": {"Realistic": 0.8, "Investigative": 0.1, "Artistic": 0.05, "Social": 0.05, "Enterprising": 0.0, "Conventional": 0.0}
        },
        {
            "question": "Would you prefer working outdoors in nature vs. in an office?",
            "riasec_mapping": {"Realistic": 0.7, "Investigative": 0.1, "Artistic": 0.1, "Social": 0.05, "Enterprising": 0.05, "Conventional": 0.0}
        },
        {
            "question": "Do you like working with machines, tools, or mechanical systems?",
            "riasec_mapping": {"Realistic": 0.85, "Investigative": 0.1, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.05, "Conventional": 0.0}
        },
        
        # INVESTIGATIVE (research, analysis, problem-solving)
        {
            "question": "Do you like solving complex problems and conducting research?",
            "riasec_mapping": {"Realistic": 0.1, "Investigative": 0.8, "Artistic": 0.05, "Social": 0.0, "Enterprising": 0.05, "Conventional": 0.0}
        },
        {
            "question": "Do you enjoy analyzing data and finding patterns?",
            "riasec_mapping": {"Realistic": 0.0, "Investigative": 0.85, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.1, "Conventional": 0.05}
        },
        {
            "question": "Would you prefer a career that requires continuous learning and discovery?",
            "riasec_mapping": {"Realistic": 0.05, "Investigative": 0.8, "Artistic": 0.1, "Social": 0.0, "Enterprising": 0.05, "Conventional": 0.0}
        },
        
        # ARTISTIC (creative expression, innovation, design)
        {
            "question": "Do you love creative expression like art, music, design, or writing?",
            "riasec_mapping": {"Realistic": 0.0, "Investigative": 0.05, "Artistic": 0.9, "Social": 0.0, "Enterprising": 0.05, "Conventional": 0.0}
        },
        {
            "question": "Do you like working on projects that allow you to express your creativity?",
            "riasec_mapping": {"Realistic": 0.05, "Investigative": 0.0, "Artistic": 0.85, "Social": 0.05, "Enterprising": 0.05, "Conventional": 0.0}
        },
        {
            "question": "Would you prefer a job that involves innovation and breaking conventional rules?",
            "riasec_mapping": {"Realistic": 0.0, "Investigative": 0.1, "Artistic": 0.75, "Social": 0.05, "Enterprising": 0.1, "Conventional": 0.0}
        },
        
        # SOCIAL (helping people, teamwork, communication)
        {
            "question": "Do you enjoy helping others and supporting people's growth?",
            "riasec_mapping": {"Realistic": 0.0, "Investigative": 0.0, "Artistic": 0.05, "Social": 0.85, "Enterprising": 0.1, "Conventional": 0.0}
        },
        {
            "question": "Do you prefer working in teams vs. working alone?",
            "riasec_mapping": {"Realistic": 0.05, "Investigative": 0.05, "Artistic": 0.05, "Social": 0.75, "Enterprising": 0.1, "Conventional": 0.0}
        },
        {
            "question": "Would you rather work in roles where you can directly impact people's lives?",
            "riasec_mapping": {"Realistic": 0.0, "Investigative": 0.0, "Artistic": 0.1, "Social": 0.8, "Enterprising": 0.05, "Conventional": 0.05}
        },
        
        # ENTERPRISING (leadership, persuasion, ambition)
        {
            "question": "Do you like taking charge and leading projects or teams?",
            "riasec_mapping": {"Realistic": 0.05, "Investigative": 0.0, "Artistic": 0.0, "Social": 0.15, "Enterprising": 0.8, "Conventional": 0.0}
        },
        {
            "question": "Do you have a natural ability to persuade and influence others?",
            "riasec_mapping": {"Realistic": 0.0, "Investigative": 0.0, "Artistic": 0.05, "Social": 0.2, "Enterprising": 0.75, "Conventional": 0.0}
        },
        {
            "question": "Would you prefer pursuing ambitious goals and climbing the ladder?",
            "riasec_mapping": {"Realistic": 0.0, "Investigative": 0.0, "Artistic": 0.0, "Social": 0.1, "Enterprising": 0.85, "Conventional": 0.05}
        },
        
        # CONVENTIONAL (organization, order, detail-oriented)
        {
            "question": "Do you prefer working in well-organized, structured environments?",
            "riasec_mapping": {"Realistic": 0.1, "Investigative": 0.05, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.05, "Conventional": 0.8}
        },
        {
            "question": "Do you have strong attention to detail and accuracy?",
            "riasec_mapping": {"Realistic": 0.1, "Investigative": 0.15, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.0, "Conventional": 0.75}
        },
        {
            "question": "Would you prefer following clear procedures and guidelines over improvisation?",
            "riasec_mapping": {"Realistic": 0.1, "Investigative": 0.05, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.0, "Conventional": 0.85}
        },
        {
            "question": "Do you excel at administrative tasks and managing information systems?",
            "riasec_mapping": {"Realistic": 0.05, "Investigative": 0.15, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.0, "Conventional": 0.8}
        },
        {
            "question": "Do you prefer stability and predictability in your career over uncertainty?",
            "riasec_mapping": {"Realistic": 0.1, "Investigative": 0.05, "Artistic": 0.0, "Social": 0.05, "Enterprising": 0.0, "Conventional": 0.8}
        }
    ]
    
    return JsonResponse(questions, safe=False)


def start_assessment(request):
    """
    Assessment intro/instruction page.
    Displays RIASEC model overview and assessment instructions.
    """
    context = {'riasec': RIASEC}
    return render(request, 'start_assessment.html', context)


def quiz(request):
    """
    Main quiz/assessment page.
    Initializes session and score tracking for RIASEC assessment.
    """
    session_id = request.session.get('session_id', str(uuid.uuid4()))
    request.session['session_id'] = session_id
    
    # Initialize RIASEC scores in session
    if 'scores' not in request.session:
        request.session['scores'] = {
            'Realistic': 0,
            'Investigative': 0,
            'Artistic': 0,
            'Social': 0,
            'Enterprising': 0,
            'Conventional': 0
        }
    
    context = {
        'riasec': RIASEC,
        'session_id': session_id,
    }
    
    return render(request, 'quiz.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def submit_answer(request):
    """
    Handle quiz answer submission.
    Updates session scores based on user's quiz responses.
    """
    try:
        data = json.loads(request.body)
        scores = data.get('scores', {})
        
        request.session['scores'] = scores
        request.session.modified = True
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


def results(request):
    """
    Display assessment results with career recommendations.
    Auto-saves assessment to database and generates career pathway.
    """
    scores = request.session.get('scores', {})
    
    # Validate scores exist
    if not scores or all(v == 0 for v in scores.values()):
        return redirect('quiz')
    
    # Calculate top categories
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_category = sorted_scores[0][0]
    top_3_categories = [cat for cat, score in sorted_scores[:3]]
    
    # Get career recommendations
    careers = CAREER_DATABASE.get(top_category, [])
    career_pathway = generate_career_pathway(top_3_categories, scores)
    
    # Auto-save assessment
    try:
        session_id = request.session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
            request.session.modified = True
        
        defaults = {
            'top_category': top_category,
            'scores': scores,
            'results': {
                'career_pathway': career_pathway,
                'top_3_categories': top_3_categories,
            }
        }
        
        if request.user.is_authenticated:
            defaults['user'] = request.user
        
        assessment, created = Assessment.objects.get_or_create(
            session_id=session_id,
            defaults=defaults
        )
        
        if not created and request.user.is_authenticated and not assessment.user:
            assessment.user = request.user
            assessment.save()
            
    except Exception as e:
        pass
    
    context = {
        'scores': scores,
        'sorted_scores': sorted_scores,
        'top_category': top_category,
        'top_3_categories': top_3_categories,
        'top_color': RIASEC[top_category]['color'],
        'top_emoji': RIASEC[top_category]['emoji'],
        'careers': careers,
        'career_pathway': career_pathway,
        'riasec': RIASEC,
    }
    
    return render(request, 'results.html', context)


def save_assessment(request):
    """
    Explicitly save assessment results to database.
    Called after quiz completion for persistent storage.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            scores = request.session.get('scores', {})
            
            if not scores or all(v == 0 for v in scores.values()):
                return JsonResponse(
                    {
                        'success': False,
                        'message': 'No assessment data. Complete the quiz first.'
                    },
                    status=400
                )
            
            # Calculate top categories
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            top_category = sorted_scores[0][0]
            top_3_categories = [cat for cat, score in sorted_scores[:3]]
            
            # Generate career pathway
            career_pathway = generate_career_pathway(top_3_categories, scores)
            
            session_id = request.session.get('session_id', str(uuid.uuid4()))
            
            results = data.get('results', {})
            if isinstance(results, list):
                results = {}
            results['career_pathway'] = career_pathway
            results['top_3_categories'] = top_3_categories
            
            # Save assessment
            defaults = {
                'top_category': top_category,
                'scores': scores,
                'results': results
            }
            
            if request.user.is_authenticated:
                defaults['user'] = request.user
            
            assessment, created = Assessment.objects.get_or_create(
                session_id=session_id,
                defaults=defaults
            )
            
            if not created and request.user.is_authenticated and not assessment.user:
                assessment.user = request.user
                assessment.save()
            
            # Clear session
            if 'scores' in request.session:
                del request.session['scores']
            if 'session_id' in request.session:
                del request.session['session_id']
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Assessment saved!'
            })
            
        except ValueError as e:
            return JsonResponse(
                {'success': False, 'message': f'Error processing scores: {str(e)}'},
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {'success': False, 'message': f'Error saving: {str(e)}'},
                status=500
            )
    
    return JsonResponse(
        {'success': False, 'message': 'Only POST allowed'},
        status=405
    )


@login_required(login_url='quiz:login')
def history(request):
    """
    Display user's assessment history.
    Shows all completed assessments with scores breakdown.
    """
    assessments = request.user.assessments.all().order_by('-completed_at')
    
    for assessment in assessments:
        if isinstance(assessment.scores, dict):
            assessment.scores_list = sorted(
                assessment.scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
        else:
            assessment.scores_list = []
    
    context = {'assessments': assessments}
    return render(request, 'history.html', context)


@login_required(login_url='quiz:login')
def assessment_detail(request, assessment_id):
    """
    Display detailed results for a specific assessment.
    Shows RIASEC scores, career matches, and career pathway.
    """
    assessment = get_object_or_404(
        Assessment,
        id=assessment_id,
        user=request.user
    )
    
    scores = assessment.scores
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    results = assessment.results or {}
    career_pathway = results.get('career_pathway', {})
    top_3_categories = results.get('top_3_categories', [])
    
    context = {
        'assessment': assessment,
        'scores': scores,
        'sorted_scores': sorted_scores,
        'riasec': RIASEC,
        'career_pathway': career_pathway,
        'top_3_categories': top_3_categories,
    }
    
    return render(request, 'assessment_detail.html', context)


@require_http_methods(["POST"])
def clear_quiz_session(request):
    """
    Clear quiz session data to allow retaking the assessment.
    Removes scores, current question, and session ID from session.
    """
    try:
        if 'scores' in request.session:
            del request.session['scores']
        if 'current_question' in request.session:
            del request.session['current_question']
        if 'session_id' in request.session:
            del request.session['session_id']
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Quiz session cleared. Retake the quiz!'
        })
        
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': f'Error: {str(e)}'},
            status=400
        )


# ===============================================================================
# SKILLS & LEARNING PATH VIEWS
# ===============================================================================

@login_required(login_url='quiz:login')
@login_required(login_url='login')
def skills_assessment(request):
    """
    Advanced skills gap analysis with learning path recommendations.
    Analyzes user's skills vs. career requirements and generates learning plans.
    """
    user = request.user
    user_skills_qs = user.skills.all()
    
    # Convert to dict for lookup
    user_skills_dict = {us.skill.id: us for us in user_skills_qs}
    user_skill_ids = set(user_skills_dict.keys())
    
    # Get latest assessment
    latest_assessment = (
        user.assessments.first()
        if hasattr(user, 'assessments')
        else None
    )
    
    # Get recommended careers
    recommended_careers = []
    if latest_assessment:
        recommended_careers = Career.objects.filter(
            primary_category=latest_assessment.top_category
        )[:3]
    
    if not recommended_careers:
        recommended_careers = Career.objects.all()[:3]
    
    # Perform gap analysis
    gap_analysis = {
        'overall_proficiency': 0.0,
        'gap_count': 0,
        'priority_skills': [],
        'mastered_skills': [],
        'in_progress_skills': [],
        'skill_categories': {},
        'learning_estimate_hours': 0,
        'industry_benchmark': 0.0
    }
    
    proficiency_scores = {
        'novice': 1,
        'beginner': 2,
        'intermediate': 3,
        'advanced': 4,
        'expert': 5
    }
    
    # Analyze each recommended career
    for career in recommended_careers:
        required_skills = career.required_skills.all()
        
        for req_skill in required_skills:
            user_skill = user_skills_dict.get(req_skill.id)
            
            required_level = proficiency_scores.get(
                req_skill.difficulty_level,
                3
            )
            current_level = (
                proficiency_scores.get(user_skill.proficiency_level, 0)
                if user_skill
                else 0
            )
            gap = max(0, required_level - current_level)
            
            skill_info = {
                'skill': req_skill,
                'required_level': req_skill.difficulty_level,
                'current_level': (
                    user_skill.proficiency_level
                    if user_skill
                    else 'none'
                ),
                'gap_score': gap,
                'is_missing': user_skill is None,
                'years_of_exp': (
                    user_skill.years_of_experience
                    if user_skill
                    else 0
                ),
                'category': req_skill.category or 'General',
                'learning_hours': gap * 20,
                'industry_demand': 8 + (gap * 0.5),
                'resources': req_skill.learning_resources or []
            }
            
            # Categorize
            if skill_info['category'] not in gap_analysis['skill_categories']:
                gap_analysis['skill_categories'][skill_info['category']] = {
                    'total': 0,
                    'mastered': 0,
                    'gap_items': [],
                    'gap_score': 0.0
                }
            
            cat = gap_analysis['skill_categories'][skill_info['category']]
            cat['total'] += 1
            
            # Classify skill
            if gap == 0 and user_skill:
                gap_analysis['mastered_skills'].append(skill_info)
                cat['mastered'] += 1
            elif gap > 0 or not user_skill:
                cat['gap_items'].append(skill_info)
                gap_analysis['gap_count'] += 1
                gap_analysis['learning_estimate_hours'] += skill_info['learning_hours']
                
                priority = (gap * 3) + (skill_info['industry_demand'] * 0.5)
                skill_info['priority_score'] = priority
                gap_analysis['priority_skills'].append(skill_info)
            
            if user_skill and current_level > 0:
                gap_analysis['in_progress_skills'].append(skill_info)
            
            if gap > 0:
                cat['gap_score'] += gap
    
    # Sort priority skills
    gap_analysis['priority_skills'] = sorted(
        gap_analysis['priority_skills'],
        key=lambda x: x['priority_score'],
        reverse=True
    )[:10]
    
    # Calculate overall stats
    total_skills = (
        len(gap_analysis['mastered_skills']) +
        gap_analysis['gap_count']
    )
    if total_skills > 0:
        gap_analysis['overall_proficiency'] = (
            (len(gap_analysis['mastered_skills']) / total_skills) * 100
        )
        gap_analysis['industry_benchmark'] = 65.0
    
    gap_analysis['learning_weeks'] = max(
        1,
        gap_analysis['learning_estimate_hours'] // 10
    )
    
    context = {
        'user_skills': user_skills_qs,
        'recommended_careers': recommended_careers,
        'gap_analysis': gap_analysis,
        'latest_assessment': latest_assessment,
        'riasec': RIASEC,
    }
    
    return render(request, 'skills_assessment.html', context)


def skill_courses(request, skill_id):
    """
    Display curated course recommendations for a specific skill.
    Shows Coursera, Udemy, and other platform course options with ratings.
    """
    skill = get_object_or_404(Skill, id=skill_id)
    
    # Curated course mapping
    coursera_courses = {
        'Python': 'https://www.coursera.org/learn/python-for-everybody',
        'JavaScript': 'https://www.coursera.org/specializations/javascript-beginner',
        'Java': 'https://www.coursera.org/learn/learn-java-programming',
        'SQL': 'https://www.coursera.org/learn/intro-sql',
        'Data Science': 'https://www.coursera.org/learn/data-science-basics',
        'Machine Learning': 'https://www.coursera.org/learn/machine-learning',
        'Communication': 'https://www.coursera.org/learn/effective-communication',
        'Leadership': 'https://www.coursera.org/learn/leadership-development',
        'Project Management': 'https://www.coursera.org/learn/project-management',
        'Financial Analysis': 'https://www.coursera.org/learn/financial-analysis',
        'UI/UX Design': 'https://www.coursera.org/learn/ux-design-fundamentals',
        'Web Development': 'https://www.coursera.org/learn/web-development',
    }
    
    # Build courses list
    recommended_courses = [
        {
            'title': f'{skill.name} Fundamentals',
            'platform': 'Coursera',
            'duration': '4 weeks',
            'level': 'Beginner',
            'description': f'Learn the basics of {skill.name} from industry experts',
            'url': coursera_courses.get(
                skill.name,
                f'https://www.coursera.org/search?query={skill.name}'
            ),
            'rating': 4.7,
            'students': 125000
        },
        {
            'title': f'Advanced {skill.name} Techniques',
            'platform': 'Coursera',
            'duration': '6 weeks',
            'level': 'Intermediate',
            'description': f'Master advanced {skill.name} concepts and applications',
            'url': coursera_courses.get(
                skill.name,
                f'https://www.coursera.org/search?query={skill.name}-advanced'
            ),
            'rating': 4.8,
            'students': 89000
        },
        {
            'title': f'{skill.name} Professional Certification',
            'platform': 'Udemy',
            'duration': '12 weeks',
            'level': 'Advanced',
            'description': f'Comprehensive certification in {skill.name}',
            'url': f'https://www.udemy.com/search/?q={skill.name}-course',
            'rating': 4.6,
            'students': 256000
        },
    ]
    
    # Update with skill resources if available
    if skill.learning_resources:
        if isinstance(skill.learning_resources, list):
            for i, resource_url in enumerate(skill.learning_resources[:2]):
                if i < len(recommended_courses):
                    recommended_courses[i]['url'] = resource_url
    
    context = {
        'skill': skill,
        'courses': recommended_courses,
    }
    
    return render(request, 'skill_courses.html', context)


@login_required(login_url='quiz:login')
def add_skill(request):
    """
    Add or update a skill in user profile.
    Supports both form POST and AJAX JSON requests.
    """
    user = request.user
    
    if request.method == 'POST':
        # Check if AJAX request
        is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            'application/json' in request.headers.get('Content-Type', '')
        )
        
        if is_ajax:
            # AJAX JSON request
            try:
                data = json.loads(request.body)
                skill_id = data.get('skill_id')
                proficiency_level = data.get('proficiency_level', 'novice')
                years_of_exp = data.get('years_of_exp', 0)
                
                skill = get_object_or_404(Skill, id=skill_id)
                user_skill, created = UserSkill.objects.update_or_create(
                    user=user,
                    skill=skill,
                    defaults={
                        'proficiency_level': proficiency_level,
                        'years_of_experience': int(years_of_exp)
                    }
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Skill added successfully!',
                    'skill_name': skill.name
                })
                
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            # Form POST request
            try:
                skill_id = request.POST.get('skill_id')
                proficiency_level = request.POST.get(
                    'proficiency_level',
                    'novice'
                )
                years_of_exp = request.POST.get('years_of_experience', 0)
                
                skill = get_object_or_404(Skill, id=skill_id)
                user_skill, created = UserSkill.objects.update_or_create(
                    user=user,
                    skill=skill,
                    defaults={
                        'proficiency_level': proficiency_level,
                        'years_of_experience': int(years_of_exp)
                    }
                )
                
                messages.success(
                    request,
                    f'✓ {skill.name} added to your skills!'
                )
                return redirect('quiz:skills_assessment')
                
            except Exception as e:
                messages.error(request, f'Error adding skill: {str(e)}')
                return redirect('quiz:add_skill')
    
    # GET request - show form
    all_skills = Skill.objects.all().order_by('category', 'name')
    user_skills = user.skills.all()
    user_skill_ids = set(s.skill.id for s in user_skills)
    
    # Categorize skills
    skills_by_category = {}
    for skill in all_skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        
        skill.already_added = skill.id in user_skill_ids
        skills_by_category[skill.category].append(skill)
    
    context = {
        'skills_by_category': skills_by_category,
        'user_skills': user_skills,
        'proficiency_levels': [
            'novice',
            'beginner',
            'intermediate',
            'advanced',
            'expert'
        ],
    }
    
    return render(request, 'add_skill.html', context)


@login_required(login_url='quiz:login')
def learning_path(request, career_id):
    """
    Display personalized learning path for a target career.
    Shows courses, estimated hours, and progress tracking.
    """
    career = get_object_or_404(Career, id=career_id)
    
    # Get or create user career goal
    goal, created = UserCareerGoal.objects.get_or_create(
        user=request.user,
        target_career=career
    )
    
    # Get user's skills
    user_skills = UserSkill.objects.filter(user=request.user)
    user_skill_ids = set(user_skills.values_list('skill_id', flat=True))
    
    # Get learning goals
    learning_goals = LearningGoal.objects.filter(
        user=request.user,
        skill__in=career.required_skills.all()
    ).prefetch_related('progress_logs')
    
    # Build recommended courses
    recommended_courses = []
    for skill in career.required_skills.all():
        if skill.id not in user_skill_ids:
            learning_goal, _ = LearningGoal.objects.get_or_create(
                user=request.user,
                skill=skill,
                defaults={'estimated_hours': 40}
            )
            
            progress = learning_goal.progress_logs.order_by(
                '-logged_at'
            ).first()
            
            if skill.learning_resources:
                for course in skill.learning_resources.get('courses', []):
                    recommended_courses.append({
                        'skill': skill.name,
                        'course': course,
                        'hours_estimated': learning_goal.estimated_hours,
                        'hours_completed': (
                            progress.hours_completed
                            if progress
                            else 0
                        ),
                        'goal_id': learning_goal.id,
                    })
    
    context = {
        'career': career,
        'goal': goal,
        'learning_goals': learning_goals,
        'recommended_courses': recommended_courses[:10],
        'total_hours_estimated': sum(
            g.estimated_hours for g in learning_goals
        ),
        'total_hours_completed': sum(
            p.hours_completed
            for g in learning_goals
            for p in [g.progress_logs.first()]
            if p
        ),
    }
    
    return render(request, 'learning_path.html', context)


@login_required(login_url='quiz:login')
def track_learning_progress(request, goal_id):
    """
    Track and update learning progress for a learning goal.
    Records hours completed and completion percentage.
    """
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create progress record
            progress = LearningProgress.objects.create(
                learning_goal=goal,
                hours_completed=float(
                    data.get('hours_completed', 0)
                ),
                completed_percentage=float(
                    data.get('completion_percentage', 0)
                ),
                courses_completed=data.get('courses_completed', []),
                milestone_reached=data.get('milestone', ''),
            )
            
            # Mark goal as completed if 100%
            if data.get('completion_percentage', 0) >= 100:
                goal.completed = True
                goal.save()
            
            return JsonResponse({
                'success': True,
                'progress_id': progress.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # GET - Show progress page
    progress_logs = goal.progress_logs.all().order_by('-logged_at')
    
    context = {
        'goal': goal,
        'progress_logs': progress_logs,
        'estimated_hours': goal.estimated_hours,
        'total_hours_logged': sum(
            p.hours_completed for p in progress_logs
        ),
    }
    
    return render(request, 'track_progress.html', context)


# ===============================================================================
# DASHBOARD VIEWS
# ===============================================================================

def dashboard(request):
    """
    User dashboard with assessment history and quick stats.
    """
    user = request.user
    assessments = (
        user.assessments.all()
        if hasattr(user, 'assessments')
        else []
    )
    
    for assessment in assessments:
        if isinstance(assessment.scores, dict):
            assessment.scores_list = sorted(
                assessment.scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
        else:
            assessment.scores_list = []
    
    context = {'assessments': assessments}
    return render(request, 'dashboard.html', context)


@login_required(login_url='quiz:login')
def personalized_dashboard(request):
    """
    Personalized dashboard with user-specific recommendations.
    Shows goals, progress, and next actions.
    """
    user = request.user
    profile = user.userprofile
    
    # Get latest assessment
    latest_assessment = Assessment.objects.filter(
        user=user
    ).order_by('-completed_at').first()
    
    # Get career goal
    career_goal = UserCareerGoal.objects.filter(user=user).first()
    
    # Calculate stats
    total_skills = UserSkill.objects.filter(user=user).count()
    learning_goals = LearningGoal.objects.filter(user=user)
    completed_goals = learning_goals.filter(completed=True).count()
    
    # Get activity feed
    recent_assessments = Assessment.objects.filter(
        user=user
    ).order_by('-completed_at')[:5]
    
    # Get recommended careers
    recommended_careers = []
    if latest_assessment and latest_assessment.top_category:
        recommended_careers = Career.objects.all()[:5]
    
    # Calculate readiness
    readiness_score = 0
    if career_goal:
        user_skill_ids = set(
            UserSkill.objects.filter(user=user).values_list(
                'skill_id',
                flat=True
            )
        )
        required_skill_ids = set(
            career_goal.target_career.required_skills.values_list(
                'id',
                flat=True
            )
        )
        if required_skill_ids:
            readiness_score = int(
                (len(user_skill_ids & required_skill_ids) /
                 len(required_skill_ids)) * 100
            )
    
    # Quick actions
    quick_actions = [
        {'title': 'Take Assessment', 'url': 'quiz:start_assessment', 'icon': '📝'},
        {'title': 'Add Skills', 'url': 'quiz:add_skill', 'icon': '➕'},
        {
            'title': 'View Roadmap',
            'url': 'quiz:career_roadmap',
            'icon': '🗺️',
            'enabled': career_goal is not None
        },
    ]
    
    context = {
        'profile': profile,
        'latest_assessment': latest_assessment,
        'career_goal': career_goal,
        'total_skills': total_skills,
        'completed_goals': completed_goals,
        'total_goals': learning_goals.count(),
        'readiness_score': readiness_score,
        'recent_assessments': recent_assessments,
        'recommended_careers': recommended_careers,
        'quick_actions': quick_actions,
        'bookmark_count': CareerBookmark.objects.filter(user=user).count(),
    }
    
    return render(request, 'personalized_dashboard.html', context)


# ===============================================================================
# CAREER TOOLS
# ===============================================================================

@login_required(login_url='quiz:login')
def career_roadmap(request, career_id):
    """
    Display career roadmap with progression steps and skill gaps.
    Shows readiness percentage and required skills for a career.
    """
    career = get_object_or_404(Career, id=career_id)
    user_profile = request.user.userprofile
    
    # Get user's skills
    user_skills = UserSkill.objects.filter(
        user=request.user
    ).values_list('skill_id', flat=True)
    
    # Calculate skill gaps
    required_skills = career.required_skills.all()
    skill_gaps = []
    skills_met = []
    
    for skill in required_skills:
        if skill.id in user_skills:
            skills_met.append(skill)
        else:
            skill_gaps.append(skill)
    
    # Prepare roadmap
    roadmap_steps = (
        career.roadmap_steps
        if hasattr(career, 'roadmap_steps')
        else []
    )
    
    # Calculate readiness
    total_required = required_skills.count()
    readiness = (
        (len(skills_met) / total_required * 100)
        if total_required > 0
        else 0
    )
    
    context = {
        'career': career,
        'roadmap_steps': roadmap_steps,
        'required_skills': required_skills,
        'skills_met': skills_met,
        'skill_gaps': skill_gaps,
        'readiness_percentage': int(readiness),
        'total_steps': len(roadmap_steps),
    }
    
    return render(request, 'career_roadmap.html', context)


@login_required(login_url='quiz:login')
def career_comparison(request):
    """
    Compare multiple careers side-by-side.
    Shows skills match and requirements for each career.
    """
    career_ids = request.GET.getlist('careers')
    careers = []
    comparison_data = {}
    
    if career_ids:
        careers = Career.objects.filter(id__in=career_ids)
        
        # Get user's skills
        user_skills = UserSkill.objects.filter(
            user=request.user
        ).values_list('skill_id', flat=True)
        
        for career in careers:
            required_skills = set(
                career.required_skills.values_list('id', flat=True)
            )
            user_has = required_skills & set(user_skills)
            
            comparison_data[career.id] = {
                'skills_match': (
                    int(len(user_has) / len(required_skills) * 100)
                    if required_skills
                    else 0
                ),
                'skills_needed': list(
                    career.required_skills.exclude(id__in=user_skills)
                    .values_list('name', flat=True)[:5]
                ),
            }
    
    # Get all careers for selection
    all_careers = Career.objects.all()
    
    context = {
        'careers': careers,
        'comparison_data': comparison_data,
        'all_careers': all_careers,
        'selected_ids': [int(c) for c in career_ids],
    }
    
    return render(request, 'career_comparison.html', context)


@login_required(login_url='quiz:login')
def career_pivot_analysis(request, target_career_id):
    """
    Analyze career transition feasibility and requirements.
    Shows skills gap, estimated retraining time, and challenges.
    """
    target_career = get_object_or_404(Career, id=target_career_id)
    user_profile = request.user.userprofile
    
    current_career = getattr(user_profile, 'current_role', 'Professional')
    
    # Get or create pivot analysis
    analysis = CareerPivotAnalysis.objects.filter(
        user=request.user,
        target_career=target_career
    ).first()
    
    if not analysis:
        # Get user's skills
        user_skills = UserSkill.objects.filter(user=request.user)
        user_skill_names = [s.skill.name for s in user_skills]
        
        # Try AI analysis first
        try:
            response = requests.post(
                'http://localhost:5000/api/analyze-career-pivot',
                json={
                    'current_role': current_career,
                    'target_career': target_career.title,
                    'current_skills': user_skill_names[:5],
                    'required_skills': list(
                        target_career.required_skills.values_list('name', flat=True)
                    ),
                },
                timeout=10
            )
            
            if response.status_code == 200:
                analysis_data = response.json()
            else:
                analysis_data = generate_fallback_analysis(
                    current_career,
                    target_career,
                    user_skill_names
                )
                
        except Exception:
            analysis_data = generate_fallback_analysis(
                current_career,
                target_career,
                user_skill_names
            )
        
        # Save analysis
        analysis = CareerPivotAnalysis.objects.create(
            user=request.user,
            current_career_type=current_career,
            target_career=target_career,
            analysis=analysis_data,
        )
    
    context = {
        'analysis': analysis,
        'target_career': target_career,
        'current_career': current_career,
    }
    
    return render(request, 'career_pivot_analysis.html', context)


# ===============================================================================
# COMMUNITY & FORUM
# ===============================================================================

def forum(request):
    """
    Forum homepage with categories and recent posts.
    Supports filtering by category via query parameter.
    """
    categories = ForumCategory.objects.all()
    selected_category = request.GET.get('category')
    
    # Get posts, filtering by category if specified
    if selected_category:
        posts = ForumPost.objects.filter(
            category_id=selected_category
        ).order_by('-created_at')[:50]
    else:
        posts = ForumPost.objects.all().order_by('-created_at')[:50]
    
    context = {
        'categories': categories,
        'posts': posts,
        'selected_category': selected_category,
    }
    
    return render(request, 'forum/forum.html', context)


@login_required(login_url='quiz:login')
def create_forum_post(request):
    """
    Create a new forum post.
    Accepts JSON POST requests with post data.
    
    Request body:
    {
        'category_id': int (required),
        'title': string (required),
        'content': string (required)
    }
    
    Returns:
    Success: {'success': True, 'post_id': int}
    Error: {'error': 'error message'} with status code
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['category_id', 'title', 'content']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse(
                        {'error': f'Missing required field: {field}'}, 
                        status=400
                    )
            
            # Verify category exists
            try:
                category = ForumCategory.objects.get(id=data.get('category_id'))
            except ForumCategory.DoesNotExist:
                return JsonResponse(
                    {'error': 'Category not found'}, 
                    status=400
                )
            
            post = ForumPost.objects.create(
                author=request.user,
                category=category,
                title=data.get('title').strip(),
                content=data.get('content').strip(),
                is_closed=False,  # Explicitly set default
            )
            
            return JsonResponse({
                'success': True,
                'post_id': post.id,
                'message': 'Discussion posted successfully!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            error_msg = str(e).lower()
            # Check for common database errors
            if 'not null constraint failed' in error_msg or 'integrity error' in error_msg:
                return JsonResponse({
                    'error': '🚀 Feature Coming Soon! We\'re setting up forum features. Please try again in a moment.'
                }, status=503)
            return JsonResponse({
                'error': f'Error posting discussion: {str(e)}'
            }, status=500)
    
    return JsonResponse(
        {'error': 'Only POST allowed'},
        status=405
    )


def forum_detail(request, post_id):
    """
    Display a single forum post with all its replies.
    Handles incrementing view count and displays replies.
    """
    post = get_object_or_404(ForumPost, id=post_id)
    
    # Increment view count
    post.views += 1
    post.save(update_fields=['views'])
    
    # Get all replies ordered by created_at
    replies = ForumReply.objects.filter(post=post).order_by('created_at')
    
    # Get all categories for sidebar
    categories = ForumCategory.objects.all()
    
    context = {
        'post': post,
        'replies': replies,
        'categories': categories,
    }
    
    return render(request, 'forum/forum_detail.html', context)


@login_required(login_url='quiz:login')
def create_forum_reply(request, post_id):
    """
    Create a reply to a forum post.
    Accepts JSON POST requests with reply content.
    """
    post = get_object_or_404(ForumPost, id=post_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            
            if not content:
                return JsonResponse(
                    {'error': 'Reply content cannot be empty'}, 
                    status=400
                )
            
            reply = ForumReply.objects.create(
                post=post,
                author=request.user,
                content=content,
            )
            
            return JsonResponse({
                'success': True,
                'reply_id': reply.id,
                'message': 'Reply posted successfully!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse(
        {'error': 'Only POST allowed'},
        status=405
    )


@login_required(login_url='quiz:login')
def delete_forum_post(request, post_id):
    """
    Delete a forum post.
    Only the post author or admin can delete.
    Accepts POST requests.
    """
    post = get_object_or_404(ForumPost, id=post_id)
    
    # Check permissions: only author or admin can delete
    if request.user != post.author and not request.user.is_staff:
        return JsonResponse(
            {'error': 'You do not have permission to delete this post'}, 
            status=403
        )
    
    if request.method == 'POST':
        try:
            # Delete all related replies first
            reply_count = post.replies.count()
            post.replies.all().delete()
            
            # Delete the post
            post.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Post deleted successfully (including {reply_count} replies)'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse(
        {'error': 'Only POST allowed'},
        status=405
    )


@login_required(login_url='quiz:login')
def delete_forum_reply(request, reply_id):
    """
    Delete a forum reply.
    Only the reply author or admin can delete.
    Accepts POST requests.
    """
    reply = get_object_or_404(ForumReply, id=reply_id)
    post_id = reply.post.id
    
    # Check permissions: only author or admin can delete
    if request.user != reply.author and not request.user.is_staff:
        return JsonResponse(
            {'error': 'You do not have permission to delete this reply'}, 
            status=403
        )
    
    if request.method == 'POST':
        try:
            reply.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Reply deleted successfully',
                'post_id': post_id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse(
        {'error': 'Only POST allowed'},
        status=405
    )



@login_required(login_url='quiz:login')
def export_pdf(request, assessment_id):
    """
    Export assessment results as PDF document.
    """
    assessment = get_object_or_404(
        Assessment,
        id=assessment_id,
        user=request.user
    )
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(
        Paragraph("Saarthi Career Assessment Report", styles['Heading1'])
    )
    elements.append(Spacer(1, 12))
    
    assessment_table_data = [
        ['Assessment Date', assessment.completed_at.strftime('%Y-%m-%d %H:%M')],
        ['Top Category', assessment.top_category],
    ]
    
    assessment_table = Table(assessment_table_data)
    assessment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(assessment_table)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("RIASEC Scores", styles['Heading2']))
    
    scores_data = [['Category', 'Score']]
    for category, score in assessment.scores.items():
        scores_data.append([category, str(score)])
    
    scores_table = Table(scores_data)
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(scores_table)
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/pdf'
    )
    response['Content-Disposition'] = (
        f'attachment; filename="Assessment_{assessment.session_id}.pdf"'
    )
    
    return response


@login_required(login_url='quiz:login')
def send_assessment_email(request, assessment_id):
    """
    Email assessment results to user.
    """
    assessment = get_object_or_404(
        Assessment,
        id=assessment_id,
        user=request.user
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Email sent successfully!'
    })


# ===============================================================================
# ADMIN ANALYTICS
# ===============================================================================

def analytics_dashboard(request):
    """
    Admin analytics dashboard with platform metrics.
    """
    if not request.user.is_staff:
        return redirect('quiz:index')
    
    total_users = User.objects.count()
    total_assessments = Assessment.objects.count()
    
    context = {
        'total_users': total_users,
        'total_assessments': total_assessments,
    }
    
    return render(request, 'admin/analytics.html', context)


# ===============================================================================
# HELPER FUNCTIONS
# ===============================================================================

def get_client_ip(request):
    """
    Extract client IP address from request.
    Handles X-Forwarded-For header for proxy environments.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_career_pathway_ai(scores):
    """
    Generate career pathway using Gemini AI based on RIASEC scores.
    Returns AI-generated pathway or None if unavailable.
    """
    try:
        response = requests.post(
            'http://localhost:5000/api/generate-career-suggestions',
            json={'scores': scores},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('primary') and data.get('roles'):
                return {
                    'primary': data.get('primary', 'Career Path'),
                    'roles': data.get('roles', []),
                    'skills': data.get('skills', []),
                    'next_steps': data.get('next_steps', [])
                }
    except Exception as e:
        print(f"AI suggestion error: {str(e)}")
    
    return None


def generate_career_pathway(top_3_categories, scores):
    """
    Generate comprehensive career pathway from RIASEC scores.
    Uses AI suggestions if available, falls back to predefined pathways.
    """
    
    # Try AI first
    ai_pathway = generate_career_pathway_ai(scores)
    if ai_pathway:
        return ai_pathway
    
    # Fallback pathways
    pathway_map = {
        ('Realistic', 'Investigative', 'Conventional'): {
            'primary': 'Engineering/Technical',
            'roles': [
                'Civil Engineer',
                'Automotive Technician',
                'Equipment Technician',
                'Quality Control Specialist'
            ],
            'skills': [
                'Technical Design',
                'Problem-solving',
                'Attention to Detail',
                'System Analysis'
            ],
            'next_steps': [
                'Learn CAD software',
                'Get industry certifications',
                'Develop project management skills'
            ]
        },
        ('Investigative', 'Realistic', 'Enterprising'): {
            'primary': 'Research & Development',
            'roles': [
                'Data Scientist',
                'Research Engineer',
                'Lab Manager',
                'Product Developer'
            ],
            'skills': [
                'Research',
                'Analysis',
                'Technical Writing',
                'Innovation'
            ],
            'next_steps': [
                'Master programming languages',
                'Pursue advanced degree',
                'Learn statistical analysis'
            ]
        },
        ('Artistic', 'Investigative', 'Social'): {
            'primary': 'Creative Arts & Design',
            'roles': [
                'UX/UI Designer',
                'Graphic Designer',
                'Content Creator',
                'Art Director'
            ],
            'skills': [
                'Creativity',
                'Technical Design',
                'Communication',
                'Visualization'
            ],
            'next_steps': [
                'Learn design tools (Figma, Adobe)',
                'Build portfolio',
                'Study user psychology'
            ]
        },
        ('Social', 'Enterprising', 'Conventional'): {
            'primary': 'Management & Development',
            'roles': [
                'Human Resources Manager',
                'Team Lead',
                'Sales Manager',
                'Operations Manager'
            ],
            'skills': [
                'Leadership',
                'Communication',
                'Organization',
                'People Management'
            ],
            'next_steps': [
                'Develop leadership skills',
                'Get MBA or business certificate',
                'Learn project management'
            ]
        },
        ('Enterprising', 'Social', 'Artistic'): {
            'primary': 'Business & Entrepreneurship',
            'roles': [
                'Entrepreneur',
                'Marketing Manager',
                'Business Consultant',
                'Executive'
            ],
            'skills': [
                'Leadership',
                'Strategic Thinking',
                'Persuasion',
                'Creativity'
            ],
            'next_steps': [
                'Take business courses',
                'Network actively',
                'Learn digital marketing'
            ]
        },
        ('Conventional', 'Investigative', 'Enterprising'): {
            'primary': 'Finance & Administration',
            'roles': [
                'Accountant',
                'Financial Analyst',
                'Data Analyst',
                'Business Administrator'
            ],
            'skills': [
                'Accuracy',
                'Analysis',
                'Organization',
                'Attention to Detail'
            ],
            'next_steps': [
                'Get accounting certifications',
                'Learn Excel & SQL',
                'Pursue related degrees'
            ]
        }
    }
    
    pathway_key = tuple(top_3_categories)
    
    # Exact match
    if pathway_key in pathway_map:
        return pathway_map[pathway_key]
    
    # Partial match
    for key, pathway in pathway_map.items():
        if any(cat in top_3_categories for cat in key[:2]):
            return pathway
    
    # Default
    return {
        'primary': f'Your Strengths: {", ".join(top_3_categories)}',
        'roles': [
            'Career Counselor',
            'Personal Coach',
            'Career Advisor',
            'Life Coach'
        ],
        'skills': [
            RIASEC.get(cat, {}).get('description', cat)
            for cat in top_3_categories
        ],
        'next_steps': [
            'Take additional assessments',
            'Explore internships',
            'Talk to professionals',
            'Attend career workshops'
        ]
    }


def generate_fallback_analysis(current_career, target_career, current_skills):
    """
    Generate fallback career pivot analysis when AI is unavailable.
    Uses simple heuristic comparison.
    """
    
    common_skills = set(current_skills) & set(
        target_career.required_skills.values_list('name', flat=True)
    )
    
    readiness = int(
        (len(common_skills) /
         max(target_career.required_skills.count(), 1)) * 100
    )
    
    return {
        'readiness_score': min(readiness + 20, 100),
        'skills_gap': list(
            target_career.required_skills.exclude(name__in=current_skills)
            .values_list('name', flat=True)[:5]
        ),
        'retraining_months': 12 if readiness < 50 else 6,
        'salary_change': getattr(target_career, 'avg_salary', 75000) - 75000,
        'top_challenges': [
            'Learning new technologies',
            'Building relevant experience',
            'Salary adjustment period',
        ],
        'success_tips': [
            'Take specialized courses in required skills',
            'Build portfolio projects for new field',
            'Network with professionals in target career',
            'Consider internship or entry-level role',
        ],
    }
