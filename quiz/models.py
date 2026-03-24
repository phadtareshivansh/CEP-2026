from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class UserProfile(models.Model):
    """Extended user profile with career interests"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    current_role = models.CharField(max_length=100, blank=True)
    experience_level = models.CharField(
        max_length=20,
        choices=[('student', 'Student'), ('entry', 'Entry Level'), ('mid', 'Mid Level'), ('senior', 'Senior')],
        default='student'
    )
    preferred_notification = models.CharField(
        max_length=20,
        choices=[('email', 'Email'), ('none', 'None')],
        default='email'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Career(models.Model):
    """Detailed career information"""
    RIASEC_CHOICES = [
        ('Realistic', 'Realistic'),
        ('Investigative', 'Investigative'),
        ('Artistic', 'Artistic'),
        ('Social', 'Social'),
        ('Enterprising', 'Enterprising'),
        ('Conventional', 'Conventional'),
    ]
    
    title = models.CharField(max_length=200, unique=True)
    primary_category = models.CharField(max_length=20, choices=RIASEC_CHOICES)
    secondary_categories = models.JSONField(default=list)  # List of secondary categories
    description = models.TextField()
    detailed_description = models.TextField(blank=True)
    average_salary_min = models.IntegerField(null=True, blank=True)
    average_salary_max = models.IntegerField(null=True, blank=True)
    job_growth_rate = models.FloatField(null=True, blank=True)  # percentage
    career_outlook = models.TextField(blank=True)
    required_education = models.CharField(max_length=200, blank=True)
    certifications = models.JSONField(default=list)
    typical_companies = models.JSONField(default=list)
    work_environment = models.TextField(blank=True)
    average_rating = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ('title',)
    
    def __str__(self):
        return self.title


class Skill(models.Model):
    """Skills required for careers"""
    SKILL_LEVEL_CHOICES = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50)  # e.g., "Technical", "Soft Skills"
    description = models.TextField(blank=True)
    difficulty_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default='intermediate')
    learning_resources = models.JSONField(default=list)  # URLs to courses etc
    careers = models.ManyToManyField(Career, related_name='required_skills')
    
    def __str__(self):
        return self.name


class UserSkill(models.Model):
    """User's skill proficiency"""
    PROFICIENCY_CHOICES = [
        ('novice', 'Novice'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='novice')
    years_of_experience = models.FloatField(default=0)
    acquired_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'skill')
    
    def __str__(self):
        return f"{self.user.username} - {self.skill.name}"


class Assessment(models.Model):
    """Store assessment history for users"""
    RIASEC_CHOICES = [
        ('Realistic', 'Realistic'),
        ('Investigative', 'Investigative'),
        ('Artistic', 'Artistic'),
        ('Social', 'Social'),
        ('Enterprising', 'Enterprising'),
        ('Conventional', 'Conventional'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments', null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    top_category = models.CharField(max_length=20, choices=RIASEC_CHOICES)
    scores = models.JSONField()  # Store all RIASEC scores
    results = models.JSONField()  # Store career recommendations
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"Assessment {self.session_id} - {self.top_category} ({self.completed_at.strftime('%Y-%m-%d')})"


class CareerRoadmap(models.Model):
    """Step-by-step roadmap to transition into a career"""
    career = models.OneToOneField(Career, on_delete=models.CASCADE, related_name='roadmap')
    timeline_months = models.IntegerField(default=12)
    steps = models.JSONField(default=list)  # List of steps with details
    estimated_cost = models.IntegerField(null=True, blank=True)
    resources = models.JSONField(default=list)  # Learning resources
    success_tips = models.JSONField(default=list)
    
    def __str__(self):
        return f"Roadmap: {self.career.title}"


class CareerBookmark(models.Model):
    """Users can bookmark careers they're interested in"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    career = models.ForeignKey(Career, on_delete=models.CASCADE)
    bookmarked_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('user', 'career')
    
    def __str__(self):
        return f"{self.user.username} bookmarked {self.career.title}"


class JobListing(models.Model):
    """Job openings related to careers"""
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='job_listings')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    required_skills = models.ManyToManyField(Skill)
    job_url = models.URLField()
    source = models.CharField(max_length=50)  # LinkedIn, Indeed, etc
    posted_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-posted_at']
    
    def __str__(self):
        return f"{self.title} at {self.company}"


class Mentor(models.Model):
    """Mentor profiles for career guidance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    specialization = models.ForeignKey(Career, on_delete=models.SET_NULL, null=True)
    bio = models.TextField()
    years_experience = models.IntegerField()
    hourly_rate = models.IntegerField(null=True, blank=True)
    availability = models.JSONField(default=list)  # Time slots
    average_rating = models.FloatField(default=0.0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Mentor: {self.user.username} - {self.specialization}"


class MentorRequest(models.Model):
    """Connection between mentee and mentor"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_requests_made')
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='mentee_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Mentorship Request: {self.mentee.username} -> {self.mentor.user.username}"


class ForumCategory(models.Model):
    """Categories for forum discussions"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name_plural = "Forum Categories"
    
    def __str__(self):
        return self.name


class ForumPost(models.Model):
    """Forum posts for community discussions"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    category = models.ForeignKey(ForumCategory, on_delete=models.SET_NULL, null=True)
    career = models.ForeignKey(Career, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=300)
    content = models.TextField()
    views = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class ForumReply(models.Model):
    """Replies to forum posts"""
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    upvotes = models.IntegerField(default=0)
    is_solution = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Reply to {self.post.title}"


class UserSuccessStory(models.Model):
    """Success stories from people in careers"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='success_stories')
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='success_stories')
    title = models.CharField(max_length=300)
    story = models.TextField()
    current_role = models.CharField(max_length=200)
    years_in_career = models.IntegerField()
    challenges_faced = models.TextField(blank=True)
    tips_for_others = models.TextField()
    image = models.ImageField(upload_to='success_stories/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.username} - {self.title}"


class AnalyticsEvent(models.Model):
    """Track user events for analytics"""
    EVENT_CHOICES = [
        ('quiz_started', 'Quiz Started'),
        ('quiz_completed', 'Quiz Completed'),
        ('career_viewed', 'Career Viewed'),
        ('career_bookmarked', 'Career Bookmarked'),
        ('job_clicked', 'Job Clicked'),
        ('mentor_contacted', 'Mentor Contacted'),
        ('forum_post_created', 'Forum Post Created'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_events', null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    career = models.ForeignKey(Career, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"


class LoginAttempt(models.Model):
    """ERP-style login attempt tracking for account lockout"""
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True)  # e.g., "Invalid password", "Account locked"
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username', '-timestamp']),
        ]
    
    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"{self.username} - {status} - {self.timestamp}"

