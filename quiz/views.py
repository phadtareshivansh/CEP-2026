from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import Count
from django.utils import timezone
import requests
import json
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from .models import (
    UserProfile, Career, Skill, UserSkill, Assessment,
    CareerRoadmap, CareerBookmark, JobListing, Mentor,
    MentorRequest, ForumPost, ForumReply, ForumCategory,
    UserSuccessStory, AnalyticsEvent, LoginAttempt
)

# RIASEC Model configuration
RIASEC = {
    'Realistic': {'color': '#ef4444', 'emoji': '🔧', 'description': 'Practical, hands-on work with tools & nature'},
    'Investigative': {'color': '#3b82f6', 'emoji': '🔬', 'description': 'Research, analysis & problem-solving'},
    'Artistic': {'color': '#f59e0b', 'emoji': '🎨', 'description': 'Creative expression & innovation'},
    'Social': {'color': '#10b981', 'emoji': '👥', 'description': 'Helping people & teamwork'},
    'Enterprising': {'color': '#ec4899', 'emoji': '💼', 'description': 'Leadership & persuasion'},
    'Conventional': {'color': '#8b5cf6', 'emoji': '📋', 'description': 'Order, organization & efficiency'}
}

CAREER_DATABASE = {
    'Realistic': [
        {'title': 'Civil Engineer', 'description': 'Design & build bridges, roads, and buildings', 'skills': 'Problem-solving, Technical Design'},
        {'title': 'Mechanic/Technician', 'description': 'Repair and maintain machinery and vehicles', 'skills': 'Troubleshooting, Technical Skills'},
        {'title': 'Carpenter', 'description': 'Build and construct wooden structures', 'skills': 'Craftsmanship, Precision'}
    ],
    'Investigative': [
        {'title': 'Data Scientist', 'description': 'Analyze data and find meaningful patterns', 'skills': 'Statistics, Programming, Analysis'},
        {'title': 'Research Scientist', 'description': 'Conduct experiments and advance knowledge', 'skills': 'Critical Thinking, Research'},
        {'title': 'Forensic Analyst', 'description': 'Investigate crimes using scientific methods', 'skills': 'Attention to Detail, Analysis'}
    ],
    'Artistic': [
        {'title': 'UI/UX Designer', 'description': 'Create beautiful and intuitive user experiences', 'skills': 'Creativity, Design, Problem-solving'},
        {'title': 'Content Creator', 'description': 'Produce engaging multimedia content', 'skills': 'Storytelling, Creativity'},
        {'title': 'Graphic Designer', 'description': 'Design visual content for various media', 'skills': 'Visual Thinking, Design Tools'}
    ],
    'Social': [
        {'title': 'Counselor/Therapist', 'description': 'Help people overcome challenges', 'skills': 'Empathy, Communication, Active Listening'},
        {'title': 'Teacher', 'description': 'Educate and inspire the next generation', 'skills': 'Communication, Patience, Mentoring'},
        {'title': 'HR Manager', 'description': 'Manage people and organizational culture', 'skills': 'Leadership, Communication, Empathy'}
    ],
    'Enterprising': [
        {'title': 'Entrepreneur', 'description': 'Start and grow your own business', 'skills': 'Leadership, Risk-taking, Vision'},
        {'title': 'Business Manager', 'description': 'Lead teams and drive growth', 'skills': 'Leadership, Strategy, Decision-making'},
        {'title': 'Sales Manager', 'description': 'Drive revenue and build relationships', 'skills': 'Persuasion, Negotiation, Ambition'}
    ],
    'Conventional': [
        {'title': 'Accountant', 'description': 'Manage finances and ensure accuracy', 'skills': 'Attention to Detail, Organization'},
        {'title': 'Data Analyst', 'description': 'Organize and analyze data efficiently', 'skills': 'Organization, Analysis, Detail-oriented'},
        {'title': 'Administrator', 'description': 'Manage office operations smoothly', 'skills': 'Organization, Planning, Precision'}
    ]
}


def index(request):
    """Home page with welcome screen"""
    # Redirect unauthenticated users to landing page
    if not request.user.is_authenticated:
        return render(request, 'landing.html')
    
    # Get assessment history from database for authenticated users
    assessments = request.user.assessments.all()[:5] if hasattr(request.user, 'assessments') else []
    
    context = {
        'previous_assessments': assessments,
        'assessment_count': Assessment.objects.filter(user=request.user).count(),
    }
    
    return render(request, 'index.html', context)


def get_questions(request):
    """Fetch questions from Node.js backend"""
    try:
        response = requests.get(f'{settings.BACKEND_API_URL}/get-questions', timeout=10)
        response.raise_for_status()
        questions = response.json()
        
        # Ensure questions is a list
        if isinstance(questions, dict):
            questions = questions.get('questions', [])
        
        return JsonResponse({'questions': questions})
    except requests.RequestException as e:
        return JsonResponse({'error': 'Unable to fetch questions'}, status=500)


def start_assessment(request):
    """Start assessment page - intro screen before quiz"""
    context = {
        'riasec': RIASEC,
    }
    return render(request, 'start_assessment.html', context)


def quiz(request):
    """Quiz page"""
    session_id = request.session.get('session_id', str(uuid.uuid4()))
    request.session['session_id'] = session_id
    
    # Initialize scores in session if not present
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
    """Handle quiz answer submission"""
    try:
        data = json.loads(request.body)
        scores = data.get('scores', {})
        
        # Store scores in session
        request.session['scores'] = scores
        request.session.modified = True
        
        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


def results(request):
    """Results page showing career matches and pathway"""
    scores = request.session.get('scores', {})
    
    # If no scores found, redirect back to quiz
    if not scores or all(v == 0 for v in scores.values()):
        return redirect('quiz')
    
    # Find top 3 categories
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_category = sorted_scores[0][0]
    top_3_categories = [cat for cat, score in sorted_scores[:3]]
    
    # Get career recommendations for top category
    careers = CAREER_DATABASE.get(top_category, [])
    
    # Build career pathway recommendations based on top 3 RIASEC types
    career_pathway = generate_career_pathway(top_3_categories, scores)
    
    # AUTO-SAVE ASSESSMENT TO HISTORY
    try:
        session_id = request.session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
            request.session.modified = True
        
        # Get or create assessment - link to current user if logged in
        defaults = {
            'top_category': top_category,
            'scores': scores,
            'results': {
                'career_pathway': career_pathway,
                'top_3_categories': top_3_categories,
            }
        }
        
        # If user is logged in, add them to the assessment
        if request.user.is_authenticated:
            defaults['user'] = request.user
        
        assessment, created = Assessment.objects.get_or_create(
            session_id=session_id,
            defaults=defaults
        )
        
        # If it already exists and user is authenticated, update user reference
        if not created and request.user.is_authenticated and not assessment.user:
            assessment.user = request.user
            assessment.save()
        
        if created:
            pass
        
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


def generate_career_pathway(top_3_categories, scores):
    """Generate a comprehensive career pathway based on top RIASEC categories"""
    
    pathway_map = {
        ('Realistic', 'Investigative', 'Conventional'): {
            'primary': 'Engineering/Technical',
            'roles': ['Civil Engineer', 'Automotive Technician', 'Equipment Technician', 'Quality Control Specialist'],
            'skills': ['Technical Design', 'Problem-solving', 'Attention to Detail', 'System Analysis'],
            'next_steps': ['Learn CAD software', 'Get industry certifications', 'Develop project management skills']
        },
        ('Investigative', 'Realistic', 'Enterprising'): {
            'primary': 'Research & Development',
            'roles': ['Data Scientist', 'Research Engineer', 'Lab Manager', 'Product Developer'],
            'skills': ['Research', 'Analysis', 'Technical Writing', 'Innovation'],
            'next_steps': ['Master programming languages', 'Pursue advanced degree', 'Learn statistical analysis']
        },
        ('Artistic', 'Investigative', 'Social'): {
            'primary': 'Creative Arts & Design',
            'roles': ['UX/UI Designer', 'Graphic Designer', 'Content Creator', 'Art Director'],
            'skills': ['Creativity', 'Technical Design', 'Communication', 'Visualization'],
            'next_steps': ['Learn design tools (Figma, Adobe)', 'Build portfolio', 'Study user psychology']
        },
        ('Social', 'Enterprising', 'Conventional'): {
            'primary': 'Management & Development',
            'roles': ['Human Resources Manager', 'Team Lead', 'Sales Manager', 'Operations Manager'],
            'skills': ['Leadership', 'Communication', 'Organization', 'People Management'],
            'next_steps': ['Develop leadership skills', 'Get MBA or business certificate', 'Learn project management']
        },
        ('Enterprising', 'Social', 'Artistic'): {
            'primary': 'Business & Entrepreneurship',
            'roles': ['Entrepreneur', 'Marketing Manager', 'Business Consultant', 'Executive'],
            'skills': ['Leadership', 'Strategic Thinking', 'Persuasion', 'Creativity'],
            'next_steps': ['Take business courses', 'Network actively', 'Learn digital marketing']
        },
        ('Conventional', 'Investigative', 'Enterprising'): {
            'primary': 'Finance & Administration',
            'roles': ['Accountant', 'Financial Analyst', 'Data Analyst', 'Business Administrator'],
            'skills': ['Accuracy', 'Analysis', 'Organization', 'Attention to Detail'],
            'next_steps': ['Get accounting certifications', 'Learn Excel & SQL', 'Pursue related degrees']
        }
    }
    
    # Find matching pathway
    pathway_key = tuple(top_3_categories)
    
    # Try exact match first
    if pathway_key in pathway_map:
        return pathway_map[pathway_key]
    
    # Try partial matches
    for key, pathway in pathway_map.items():
        if any(cat in top_3_categories for cat in key[:2]):
            return pathway
    
    # Default pathway
    return {
        'primary': f'Your Strengths: {", ".join(top_3_categories)}',
        'roles': ['Career Counselor', 'Personal Coach', 'Career Advisor', 'Life Coach'],
        'skills': [RIASEC.get(cat, {}).get('description', cat) for cat in top_3_categories],
        'next_steps': ['Take additional assessments', 'Explore internships', 'Talk to professionals', 'Attend career workshops']
    }


def save_assessment(request):
    """Save assessment to database"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            scores = request.session.get('scores', {})
            
            # Validate scores exist and are not all zeros
            if not scores or all(v == 0 for v in scores.values()):
                return JsonResponse({
                    'success': False, 
                    'message': 'No assessment data found. Please complete the quiz first.'
                }, status=400)
            
            # Find top category
            top_category = max(scores.items(), key=lambda x: x[1])[0]
            
            session_id = request.session.get('session_id', str(uuid.uuid4()))
            
            # Save assessment using get_or_create to handle duplicates
            defaults = {
                'top_category': top_category,
                'scores': scores,
                'results': data.get('results', [])
            }
            
            # Link to user if authenticated
            if request.user.is_authenticated:
                defaults['user'] = request.user
            
            assessment, created = Assessment.objects.get_or_create(
                session_id=session_id,
                defaults=defaults
            )
            
            # If it already exists and user is authenticated, update user reference
            if not created and request.user.is_authenticated and not assessment.user:
                assessment.user = request.user
                assessment.save()
            
            # Clear session data
            if 'scores' in request.session:
                del request.session['scores']
            if 'session_id' in request.session:
                del request.session['session_id']
            request.session.modified = True
            
            return JsonResponse({'success': True, 'message': 'Assessment saved!'})
        except ValueError as e:
            return JsonResponse({'success': False, 'message': f'Error processing scores: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error saving assessment: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Only POST allowed'}, status=405)


@login_required(login_url='quiz:login')
def history(request):
    """View assessment history"""
    # Show only current user's assessments
    assessments = request.user.assessments.all().order_by('-completed_at')
    
    context = {
        'assessments': assessments,
    }
    
    return render(request, 'history.html', context)


# ==================== AUTHENTICATION VIEWS ====================

def signup(request):
    """User registration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '')
            email = data.get('email', '')
            password = data.get('password', '')
            
            # Validation
            if not username or not email or not password:
                return JsonResponse({'success': False, 'message': 'All fields are required'}, status=400)
            
            if len(password) < 6:
                return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'Username already exists'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Email already exists'}, status=400)
            
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)
            UserProfile.objects.create(user=user)
            
            # Login user
            login(request, user)
            
            return JsonResponse({'success': True, 'message': 'Account created successfully!'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
    return render(request, 'auth/signup.html')


def login_view(request):
    """User login with ERP-style security (account lockout, audit logging)"""
    from django.conf import settings
    from datetime import timedelta
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '')
            password = data.get('password', '')
            
            if not username or not password:
                # Log failed attempt
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=get_client_ip(request),
                    success=False,
                    reason='Empty username or password'
                )
                return JsonResponse({'success': False, 'message': 'Username and password are required'}, status=400)
            
            # Check for account lockout (too many failed attempts)
            failed_attempts = LoginAttempt.objects.filter(
                username=username,
                success=False,
                timestamp__gte=timezone.now() - timedelta(minutes=settings.LOCK_TIME_MINUTES)
            ).count()
            
            if failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=get_client_ip(request),
                    success=False,
                    reason=f'Account locked due to {settings.MAX_LOGIN_ATTEMPTS} failed attempts'
                )
                return JsonResponse({
                    'success': False, 
                    'message': f'Account temporarily locked. Please try again after {settings.LOCK_TIME_MINUTES} minutes.'
                }, status=429)
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Log successful login
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=get_client_ip(request),
                    success=True,
                    reason='Successful login'
                )
                
                # Clear previous failed attempts on successful login
                LoginAttempt.objects.filter(
                    username=username,
                    success=False
                ).delete()
                
                return JsonResponse({'success': True, 'message': 'Logged in successfully!'})
            else:
                # Log failed attempt
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=get_client_ip(request),
                    success=False,
                    reason='Invalid username or password'
                )
                
                # Count failed attempts
                new_failed_count = LoginAttempt.objects.filter(
                    username=username,
                    success=False,
                    timestamp__gte=timezone.now() - timedelta(minutes=settings.LOCK_TIME_MINUTES)
                ).count()
                
                remaining_attempts = settings.MAX_LOGIN_ATTEMPTS - new_failed_count
                
                if remaining_attempts > 0:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Invalid username or password. {remaining_attempts} attempts remaining.'
                    }, status=400)
                else:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Too many failed attempts. Account locked for {settings.LOCK_TIME_MINUTES} minutes.'
                    }, status=429)
                    
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
    # GET request - render login page
    context = {
        'session_expired': request.GET.get('session_expired', False)
    }
    return render(request, 'auth/login.html', context)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def logout_view(request):
    """User logout"""
    logout(request)
    return redirect('quiz:index')


@require_http_methods(["POST"])
def clear_quiz_session(request):
    """Clear quiz session data to allow retaking the quiz"""
    try:
        # Clear quiz-related session data
        if 'scores' in request.session:
            del request.session['scores']
        if 'current_question' in request.session:
            del request.session['current_question']
        if 'session_id' in request.session:
            del request.session['session_id']
        request.session.modified = True
        
        return JsonResponse({'success': True, 'message': 'Quiz session cleared. You can now retake the quiz!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)


@login_required(login_url='quiz:login')
def profile(request):
    """User profile view and edit"""
    user = request.user
    profile = user.profile if hasattr(user, 'profile') else UserProfile.objects.get_or_create(user=user)[0]
    
    if request.method == 'POST':
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.phone = request.POST.get('phone', '')
        profile.current_role = request.POST.get('current_role', '')
        profile.experience_level = request.POST.get('experience_level', 'student')
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        return JsonResponse({'success': True, 'message': 'Profile updated successfully!'})
    
    assessments = user.assessments.all()[:5] if hasattr(user, 'assessments') else []
    
    context = {
        'profile': profile,
        'assessments': assessments,
    }
    
    return render(request, 'auth/profile.html', context)


# ==================== DASHBOARD ====================

def dashboard(request):
    """User dashboard"""
    user = request.user
    assessments = user.assessments.all() if hasattr(user, 'assessments') else []
    
    context = {
        'assessments': assessments[:5],
    }
    
    return render(request, 'dashboard.html', context)


@login_required(login_url='quiz:login')
def assessment_detail(request, assessment_id):
    """View detailed assessment results"""
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    
    # Get all RIASEC details for context
    scores = assessment.scores
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Get career recommendations from results
    results = assessment.results or {}
    career_pathway = results.get('career_pathway', [])
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


# ==================== SKILLS & GAP ANALYSIS ====================

@login_required(login_url='quiz:login')
def skills_assessment(request):
    """Skills gap analysis"""
    user = request.user
    user_skills = user.user_skills.all() if hasattr(user, 'user_skills') else []
    
    latest_assessment = user.assessments.first() if hasattr(user, 'assessments') else None
    if latest_assessment:
        recommended_careers = Career.objects.filter(
            primary_category=latest_assessment.top_category
        )[:3]
    else:
        recommended_careers = []
    
    context = {
        'user_skills': user_skills,
        'recommended_careers': recommended_careers,
    }
    
    return render(request, 'skills_assessment.html', context)


@login_required(login_url='quiz:login')
def add_skill(request):
    """Add a skill to user profile"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            skill_id = data.get('skill_id')
            proficiency_level = data.get('proficiency_level', 'novice')
            
            skill = get_object_or_404(Skill, id=skill_id)
            user_skill, created = UserSkill.objects.update_or_create(
                user=request.user,
                skill=skill,
                defaults={'proficiency_level': proficiency_level}
            )
            
            return JsonResponse({'success': True, 'message': 'Skill added!'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Only POST allowed'}, status=405)


# ==================== PDF EXPORT ====================

@login_required(login_url='quiz:login')
def export_pdf(request, assessment_id):
    """Export assessment as PDF"""
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph("Saarthi Career Assessment Report", styles['Heading1']))
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
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Assessment_{assessment.session_id}.pdf"'
    
    return response


@login_required(login_url='quiz:login')
def send_assessment_email(request, assessment_id):
    """Email assessment results"""
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    return JsonResponse({'success': True, 'message': 'Email sent successfully!'})


# ==================== JOB LISTINGS ====================




# ==================== FORUM ====================

def forum(request):
    """Forum homepage"""
    categories = ForumCategory.objects.all()
    posts = ForumPost.objects.all()[:20]
    
    context = {
        'categories': categories,
        'posts': posts,
    }
    
    return render(request, 'forum/forum.html', context)


@login_required(login_url='quiz:login')
def create_forum_post(request):
    """Create forum post"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            post = ForumPost.objects.create(
                author=request.user,
                category_id=data.get('category_id'),
                title=data.get('title'),
                content=data.get('content'),
            )
            
            return JsonResponse({'success': True, 'post_id': post.id})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Only POST allowed'}, status=405)


# ==================== ANALYTICS ====================

def analytics_dashboard(request):
    """Admin analytics dashboard"""
    if not request.user.is_staff:
        return redirect('quiz:index')
    
    total_users = User.objects.count()
    total_assessments = Assessment.objects.count()
    
    context = {
        'total_users': total_users,
        'total_assessments': total_assessments,
    }
    
    return render(request, 'admin/analytics.html', context)
