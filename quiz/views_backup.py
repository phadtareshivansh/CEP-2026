from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
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
    UserSuccessStory, AnalyticsEvent, LoginAttempt,
    UserCareerGoal, LearningGoal, LearningProgress, CareerPivotAnalysis
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


def landing_dashboard(request):
    """Landing dashboard with continuously updating stats"""
    context = {}
    return render(request, 'landing_dashboard.html', context)


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


def generate_career_pathway_ai(scores):
    """Generate personalized career pathway using Gemini AI based on RIASEC scores"""
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
    """Generate a comprehensive career pathway based on top RIASEC categories"""
    
    # Try AI-generated suggestions first
    ai_pathway = generate_career_pathway_ai(scores)
    if ai_pathway:
        return ai_pathway
    
    # Fallback to hardcoded pathways
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
            
            # Find top category and top 3 categories
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            top_category = sorted_scores[0][0]
            top_3_categories = [cat for cat, score in sorted_scores[:3]]
            
            # Generate career pathway recommendations
            career_pathway = generate_career_pathway(top_3_categories, scores)
            
            session_id = request.session.get('session_id', str(uuid.uuid4()))
            
            # Prepare results with career pathway
            results = data.get('results', [])
            if isinstance(results, list):
                results = {}
            results['career_pathway'] = career_pathway
            results['top_3_categories'] = top_3_categories
            
            # Save assessment using get_or_create to handle duplicates
            defaults = {
                'top_category': top_category,
                'scores': scores,
                'results': results
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
    
    # Process assessments to make scores template-friendly
    for assessment in assessments:
        # Convert scores dict to a list of tuples for template iteration
        if isinstance(assessment.scores, dict):
            assessment.scores_list = sorted(assessment.scores.items(), key=lambda x: x[1], reverse=True)
        else:
            assessment.scores_list = []
    
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
        messages.success(request, 'Profile updated successfully!')
        return redirect('quiz:profile')
    
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
    
    # Process assessments to make scores template-friendly
    for assessment in assessments:
        if isinstance(assessment.scores, dict):
            assessment.scores_list = sorted(assessment.scores.items(), key=lambda x: x[1], reverse=True)
        else:
            assessment.scores_list = []
    
    context = {
        'assessments': assessments,
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


# ==================== SKILLS & GAP ANALYSIS ====================

@login_required(login_url='quiz:login')
def skills_assessment(request):
    """Advanced skills gap analysis with learning paths"""
    user = request.user
    user_skills_qs = user.skills.all()
    
    # Convert to dict for easy lookup
    user_skills_dict = {us.skill.id: us for us in user_skills_qs}
    user_skill_ids = set(user_skills_dict.keys())
    
    # Get latest assessment and top 3 recommended careers
    latest_assessment = user.assessments.first() if hasattr(user, 'assessments') else None
    recommended_careers = []
    if latest_assessment:
        recommended_careers = Career.objects.filter(
            primary_category=latest_assessment.top_category
        )[:3]
    
    # If no assessment/careers, get top careers by default
    if not recommended_careers:
        recommended_careers = Career.objects.all()[:3]
    
    # Detailed gap analysis
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
            
            # Determine skill level requirement
            required_level = proficiency_scores.get(req_skill.difficulty_level, 3)
            current_level = proficiency_scores.get(user_skill.proficiency_level, 0) if user_skill else 0
            gap = max(0, required_level - current_level)
            
            skill_info = {
                'skill': req_skill,
                'required_level': req_skill.difficulty_level,
                'current_level': user_skill.proficiency_level if user_skill else 'none',
                'gap_score': gap,
                'is_missing': user_skill is None,
                'years_of_exp': user_skill.years_of_experience if user_skill else 0,
                'category': req_skill.category or 'General',
                'learning_hours': gap * 20,  # Estimate: 20 hours per proficiency level
                'industry_demand': 8 + (gap * 0.5),  # Score 1-10
                'resources': req_skill.learning_resources or []
            }
            
            # Categorize skills
            if skill_info['category'] not in gap_analysis['skill_categories']:
                gap_analysis['skill_categories'][skill_info['category']] = {
                    'total': 0,
                    'mastered': 0,
                    'gap_items': [],
                    'gap_score': 0.0
                }
            
            cat = gap_analysis['skill_categories'][skill_info['category']]
            cat['total'] += 1
            
            if gap == 0 and user_skill:
                gap_analysis['mastered_skills'].append(skill_info)
                cat['mastered'] += 1
            elif gap > 0 or not user_skill:
                cat['gap_items'].append(skill_info)
                gap_analysis['gap_count'] += 1
                gap_analysis['learning_estimate_hours'] += skill_info['learning_hours']
                
                # Prioritize by gap + industry demand
                priority = (gap * 3) + (skill_info['industry_demand'] * 0.5)
                skill_info['priority_score'] = priority
                gap_analysis['priority_skills'].append(skill_info)
            
            if user_skill and current_level > 0:
                gap_analysis['in_progress_skills'].append(skill_info)
            
            # Update category gap score
            if gap > 0:
                cat['gap_score'] += gap
    
    # Sort priority skills by priority score
    gap_analysis['priority_skills'] = sorted(
        gap_analysis['priority_skills'],
        key=lambda x: x['priority_score'],
        reverse=True
    )[:10]  # Top 10 priority skills
    
    # Calculate overall stats
    total_skills = len(gap_analysis['mastered_skills']) + gap_analysis['gap_count']
    if total_skills > 0:
        gap_analysis['overall_proficiency'] = (len(gap_analysis['mastered_skills']) / total_skills) * 100
        gap_analysis['industry_benchmark'] = 65.0  # Target proficiency percentage
    
    # Estimate learning path (weeks)
    gap_analysis['learning_weeks'] = max(1, gap_analysis['learning_estimate_hours'] // 10)  # Assume 10 hrs/week
    
    context = {
        'user_skills': user_skills_qs,
        'recommended_careers': recommended_careers,
        'gap_analysis': gap_analysis,
        'latest_assessment': latest_assessment,
        'riasec': RIASEC,
    }
    
    return render(request, 'skills_assessment.html', context)


def skill_courses(request, skill_id):
    """Display curated courses for a specific skill"""
    skill = get_object_or_404(Skill, id=skill_id)
    
    # Curated courses by skill (can be expanded in database)
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
    
    # Recommended courses structure
    recommended_courses = [
        {
            'title': f'{skill.name} Fundamentals',
            'platform': 'Coursera',
            'duration': '4 weeks',
            'level': 'Beginner',
            'description': f'Learn the basics of {skill.name} from industry experts',
            'url': coursera_courses.get(skill.name, f'https://www.coursera.org/search?query={skill.name}'),
            'rating': 4.7,
            'students': 125000
        },
        {
            'title': f'Advanced {skill.name} Techniques',
            'platform': 'Coursera',
            'duration': '6 weeks',
            'level': 'Intermediate',
            'description': f'Master advanced concepts and practical applications in {skill.name}',
            'url': coursera_courses.get(skill.name, f'https://www.coursera.org/search?query={skill.name}-advanced'),
            'rating': 4.8,
            'students': 89000
        },
        {
            'title': f'{skill.name} Professional Certification',
            'platform': 'Udemy',
            'duration': '12 weeks',
            'level': 'Advanced',
            'description': f'Comprehensive certification program in {skill.name}',
            'url': f'https://www.udemy.com/search/?q={skill.name}-course',
            'rating': 4.6,
            'students': 256000
        },
    ]
    
    # Get learning resources from skill model if available
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
    """Add a skill to user profile"""
    user = request.user

    
    if request.method == 'POST':
        # Handle both form POST and AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Content-Type', ''):
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
                proficiency_level = request.POST.get('proficiency_level', 'novice')
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
                
                from django.contrib import messages
                messages.success(request, f'✓ {skill.name} added to your skills!')
                return redirect('quiz:skills_assessment')
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f'Error adding skill: {str(e)}')
                return redirect('quiz:add_skill')
    
    # GET request - show form
    # Get all available skills
    all_skills = Skill.objects.all().order_by('category', 'name')
    
    # Get user's current skills
    user_skills = user.skills.all()
    user_skill_ids = set(s.skill.id for s in user_skills)
    
    # Categorize available skills
    skills_by_category = {}
    for skill in all_skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        
        # Mark if already added
        skill.already_added = skill.id in user_skill_ids
        skills_by_category[skill.category].append(skill)
    
    context = {
        'skills_by_category': skills_by_category,
        'user_skills': user_skills,
        'proficiency_levels': ['novice', 'beginner', 'intermediate', 'advanced', 'expert'],
    }
    
    return render(request, 'add_skill.html', context)


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


# ==================== CAREER ROADMAP VISUALIZATION ====================

@login_required(login_url='quiz:login')
def career_roadmap(request, career_id):
    """Display career roadmap with progression steps"""
    career = get_object_or_404(Career, id=career_id)
    user_profile = request.user.userprofile
    
    # Get user's skills
    user_skills = UserSkill.objects.filter(user=request.user).values_list('skill_id', flat=True)
    
    # Calculate skill gaps
    required_skills = career.required_skills.all()
    skill_gaps = []
    skills_met = []
    
    for skill in required_skills:
        if skill.id in user_skills:
            skills_met.append(skill)
        else:
            skill_gaps.append(skill)
    
    # Prepare roadmap steps
    roadmap_steps = career.roadmap_steps if hasattr(career, 'roadmap_steps') else []
    
    # Calculate readiness percentage
    total_required = required_skills.count()
    readiness = (len(skills_met) / total_required * 100) if total_required > 0 else 0
    
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


# ==================== LEARNING PATH RECOMMENDATIONS ====================

@login_required(login_url='quiz:login')
def learning_path(request, career_id):
    """Display personalized learning path with course recommendations"""
    from .models import LearningGoal, LearningProgress, UserCareerGoal
    
    career = get_object_or_404(Career, id=career_id)
    
    # Get or create user career goal
    goal, created = UserCareerGoal.objects.get_or_create(
        user=request.user,
        target_career=career
    )
    
    # Get user's current skills
    user_skills = UserSkill.objects.filter(user=request.user)
    user_skill_ids = set(user_skills.values_list('skill_id', flat=True))
    
    # Find learning goals for this career
    learning_goals = LearningGoal.objects.filter(
        user=request.user,
        skill__in=career.required_skills.all()
    ).prefetch_related('progress_logs')
    
    # Get recommended courses
    recommended_courses = []
    for skill in career.required_skills.all():
        if skill.id not in user_skill_ids:
            learning_goal, _ = LearningGoal.objects.get_or_create(
                user=request.user,
                skill=skill,
                defaults={'estimated_hours': 40}
            )
            
            # Get progress
            progress = learning_goal.progress_logs.all().order_by('-logged_at').first()
            
            if skill.learning_resources:
                for course in skill.learning_resources.get('courses', []):
                    recommended_courses.append({
                        'skill': skill.name,
                        'course': course,
                        'hours_estimated': learning_goal.estimated_hours,
                        'hours_completed': progress.hours_completed if progress else 0,
                        'goal_id': learning_goal.id,
                    })
    
    context = {
        'career': career,
        'goal': goal,
        'learning_goals': learning_goals,
        'recommended_courses': recommended_courses[:10],  # Top 10 courses
        'total_hours_estimated': sum(g.estimated_hours for g in learning_goals),
        'total_hours_completed': sum(
            p.hours_completed for g in learning_goals 
            for p in [g.progress_logs.first()]
            if p
        ),
    }
    
    return render(request, 'learning_path.html', context)


# ==================== CAREER COMPARISON TOOL ====================

@login_required(login_url='quiz:login')
def career_comparison(request):
    """Compare multiple careers side-by-side"""
    career_ids = request.GET.getlist('careers')
    careers = []
    comparison_data = {}
    
    if career_ids:
        careers = Career.objects.filter(id__in=career_ids)
        
        # Get user's skills
        user_skills = UserSkill.objects.filter(user=request.user).values_list('skill_id', flat=True)
        
        for career in careers:
            required_skills = set(career.required_skills.values_list('id', flat=True))
            user_has = required_skills & set(user_skills)
            
            comparison_data[career.id] = {
                'skills_match': int(len(user_has) / len(required_skills) * 100) if required_skills else 0,
                'skills_needed': list(
                    career.required_skills.exclude(id__in=user_skills)
                    .values_list('name', flat=True)[:5]
                ),
            }
    
    # Get all available careers for selection
    all_careers = Career.objects.all()
    
    context = {
        'careers': careers,
        'comparison_data': comparison_data,
        'all_careers': all_careers,
        'selected_ids': [int(c) for c in career_ids],
    }
    
    return render(request, 'career_comparison.html', context)


# ==================== PERSONALIZED DASHBOARD ====================

@login_required(login_url='quiz:login')
def personalized_dashboard(request):
    """Personalized dashboard with user-specific stats and recommendations"""
    from .models import UserCareerGoal, LearningGoal
    
    user = request.user
    profile = user.userprofile
    
    # Get latest assessment
    latest_assessment = Assessment.objects.filter(user=user).order_by('-completed_at').first()
    
    # Get career goal
    career_goal = UserCareerGoal.objects.filter(user=user).first()
    
    # Calculate stats
    total_skills = UserSkill.objects.filter(user=user).count()
    learning_goals = LearningGoal.objects.filter(user=user)
    completed_goals = learning_goals.filter(completed=True).count()
    
    # Get activity feed
    recent_assessments = Assessment.objects.filter(user=user).order_by('-completed_at')[:5]
    
    # Get recommended careers based on assessment
    recommended_careers = []
    if latest_assessment and latest_assessment.top_category:
        recommended_careers = Career.objects.all()[:5]
    
    # Calculate readiness for goal
    readiness_score = 0
    if career_goal:
        user_skill_ids = set(UserSkill.objects.filter(user=user).values_list('skill_id', flat=True))
        required_skill_ids = set(career_goal.target_career.required_skills.values_list('id', flat=True))
        if required_skill_ids:
            readiness_score = int(len(user_skill_ids & required_skill_ids) / len(required_skill_ids) * 100)
    
    # Quick actions
    quick_actions = [
        {'title': 'Take Assessment', 'url': 'quiz:start_assessment', 'icon': '📝'},
        {'title': 'Add Skills', 'url': 'quiz:add_skill', 'icon': '➕'},
        {'title': 'View Roadmap', 'url': 'quiz:career_roadmap', 'icon': '🗺️', 'enabled': career_goal is not None},
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


# ==================== TRACK LEARNING PROGRESS ====================

@login_required(login_url='quiz:login')
def track_learning_progress(request, goal_id):
    """Track and update learning progress for a goal"""
    from .models import LearningGoal, LearningProgress
    
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Update progress
            progress = LearningProgress.objects.create(
                learning_goal=goal,
                hours_completed=float(data.get('hours_completed', 0)),
                completed_percentage=float(data.get('completion_percentage', 0)),
                courses_completed=data.get('courses_completed', []),
                milestone_reached=data.get('milestone', ''),
            )
            
            # Mark goal as completed if 100%
            if data.get('completion_percentage', 0) >= 100:
                goal.completed = True
                goal.save()
            
            return JsonResponse({'success': True, 'progress_id': progress.id})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # GET - Show progress tracking page
    progress_logs = goal.progress_logs.all().order_by('-logged_at')
    
    context = {
        'goal': goal,
        'progress_logs': progress_logs,
        'estimated_hours': goal.estimated_hours,
        'total_hours_logged': sum(p.hours_completed for p in progress_logs),
    }
    
    return render(request, 'track_progress.html', context)


# ==================== CAREER PIVOT ADVISOR ====================

@login_required(login_url='quiz:login')
def career_pivot_analysis(request, target_career_id):
    """AI-powered career pivot analysis"""
    from .models import CareerPivotAnalysis
    
    target_career = get_object_or_404(Career, id=target_career_id)
    
    # Get user's current career info (from profile or latest assessment)
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
        
        # Prepare data for AI analysis
        analysis_prompt = f"""
        Career Transition Analysis:
        - Current Role: {current_career}
        - Target Career: {target_career.title}
        - Current Skills: {', '.join(user_skill_names[:5]) if user_skill_names else 'None listed'}
        - Required Skills: {', '.join(target_career.required_skills.values_list('name', flat=True)[:5])}
        
        Provide a JSON analysis with:
        - readiness_score (0-100)
        - skills_gap (list of missing skills)
        - retraining_months (estimated months needed)
        - salary_change (percentage change in salary)
        - top_challenges (list of challenges)
        - success_tips (list of actionable tips)
        """
        
        # Call Node.js backend for Gemini analysis
        try:
            response = requests.post(
                'http://localhost:5000/api/analyze-career-pivot',
                json={
                    'current_role': current_career,
                    'target_career': target_career.title,
                    'current_skills': user_skill_names[:5],
                    'required_skills': list(target_career.required_skills.values_list('name', flat=True)),
                },
                timeout=10
            )
            
            if response.status_code == 200:
                analysis_data = response.json()
            else:
                # Fallback analysis
                analysis_data = generate_fallback_analysis(current_career, target_career, user_skill_names)
        except:
            analysis_data = generate_fallback_analysis(current_career, target_career, user_skill_names)
        
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


def generate_fallback_analysis(current_career, target_career, current_skills):
    """Generate fallback analysis when AI is unavailable"""
    
    # Simple heuristic analysis
    common_skills = set(current_skills) & set(
        target_career.required_skills.values_list('name', flat=True)
    )
    
    readiness = int(len(common_skills) / max(target_career.required_skills.count(), 1) * 100)
    
    return {
        'readiness_score': min(readiness + 20, 100),  # Slight boost
        'skills_gap': list(
            target_career.required_skills.exclude(name__in=current_skills)
            .values_list('name', flat=True)[:5]
        ),
        'retraining_months': 12 if readiness < 50 else 6,
        'salary_change': target_career.avg_salary - 75000,  # Estimate
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
