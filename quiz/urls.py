"""
Saarthi URL Configuration Module

This module defines all URL paths for the Saarthi career guidance platform.
URLs are organized into logical sections for easy navigation and maintenance:

- Home & Landing Pages
- Authentication & User Management
- Assessment & Quiz Pages
- Skills & Learning Paths
- Career Tools (Comparison, Roadmap, Pivot Analysis)
- Community & Forum
- Export & Utilities
- Admin & API

Each section is clearly marked with comments for easy code navigation.
"""

from django.urls import path

from . import views
from .views_migrations import trigger_migrations

app_name = 'quiz'

urlpatterns = [
    # ===================================================================
    # HOME & LANDING PAGES
    # ===================================================================
    path('', views.index, name='index'),
    path('landing/', views.landing_dashboard, name='landing_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/personalized/', views.personalized_dashboard, name='personalized_dashboard'),

    # ===================================================================
    # AUTHENTICATION & USER MANAGEMENT
    # ===================================================================
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),

    # ===================================================================
    # ASSESSMENT & QUIZ PAGES
    # ===================================================================
    path('start-assessment/', views.start_assessment, name='start_assessment'),
    path('quiz/', views.quiz, name='quiz'),
    path('results/', views.results, name='results'),
    path('history/', views.history, name='history'),
    path('assessment/<int:assessment_id>/', views.assessment_detail, name='assessment_detail'),

    # ===================================================================
    # QUIZ API ENDPOINTS
    # ===================================================================
    path('api/get-questions/', views.get_questions, name='get_questions'),
    path('api/submit-answer/', views.submit_answer, name='submit_answer'),
    path('api/save-assessment/', views.save_assessment, name='save_assessment'),
    path('api/clear-quiz-session/', views.clear_quiz_session, name='clear_quiz_session'),

    # ===================================================================
    # SKILLS & LEARNING PATHS
    # ===================================================================
    path('skills/', views.skills_assessment, name='skills_assessment'),
    path('skills/<int:skill_id>/courses/', views.skill_courses, name='skill_courses'),
    path('career/<int:career_id>/learning-path/', views.learning_path, name='learning_path'),
    path('learning-progress/<int:goal_id>/', views.track_learning_progress, name='track_progress'),

    # ===================================================================
    # SKILLS API ENDPOINTS
    # ===================================================================
    path('api/add-skill/', views.add_skill, name='add_skill'),

    # ===================================================================
    # CAREER TOOLS
    # ===================================================================
    path('career/<int:career_id>/roadmap/', views.career_roadmap, name='career_roadmap'),
    path('career/compare/', views.career_comparison, name='career_comparison'),
    path('career/<int:target_career_id>/pivot-analysis/', views.career_pivot_analysis, name='career_pivot_analysis'),

    # ===================================================================
    # COMMUNITY & FORUM
    # ===================================================================
    path('forum/', views.forum, name='forum'),
    path('forum/<int:post_id>/', views.forum_detail, name='forum_detail'),
    path('api/forum/post/create/', views.create_forum_post, name='create_forum_post'),
    path('api/forum/<int:post_id>/reply/', views.create_forum_reply, name='create_forum_reply'),
    path('api/forum/<int:post_id>/delete/', views.delete_forum_post, name='delete_forum_post'),
    path('api/forum/reply/<int:reply_id>/delete/', views.delete_forum_reply, name='delete_forum_reply'),

    # ===================================================================
    # EXPORT & UTILITIES
    # ===================================================================
    path('export/pdf/<int:assessment_id>/', views.export_pdf, name='export_pdf'),
    path('api/email/<int:assessment_id>/', views.send_assessment_email, name='send_email'),

    # ===================================================================
    # ADMIN & SYSTEM
    # ===================================================================
    path('admin/analytics/', views.analytics_dashboard, name='analytics'),
    path('api/migrations/', trigger_migrations, name='trigger_migrations'),
]

