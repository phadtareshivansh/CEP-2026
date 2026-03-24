from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # Home & Auth
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Quiz
    path('start-assessment/', views.start_assessment, name='start_assessment'),
    path('quiz/', views.quiz, name='quiz'),
    path('api/get-questions/', views.get_questions, name='get_questions'),
    path('api/submit-answer/', views.submit_answer, name='submit_answer'),
    path('results/', views.results, name='results'),
    path('api/save-assessment/', views.save_assessment, name='save_assessment'),
    path('api/clear-quiz-session/', views.clear_quiz_session, name='clear_quiz_session'),
    path('history/', views.history, name='history'),
    path('assessment/<int:assessment_id>/', views.assessment_detail, name='assessment_detail'),
    
    # Skills
    path('skills/', views.skills_assessment, name='skills_assessment'),
    path('api/add-skill/', views.add_skill, name='add_skill'),
    
    # Export
    path('export/pdf/<int:assessment_id>/', views.export_pdf, name='export_pdf'),
    path('api/email/<int:assessment_id>/', views.send_assessment_email, name='send_email'),
    
    # Forum
    path('forum/', views.forum, name='forum'),
    path('api/forum/post/create/', views.create_forum_post, name='create_forum_post'),
    
    # Analytics
    path('admin/analytics/', views.analytics_dashboard, name='analytics'),
]
