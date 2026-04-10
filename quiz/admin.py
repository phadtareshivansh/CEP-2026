from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserProfile, Career, Skill, UserSkill, Assessment,
    CareerRoadmap, CareerBookmark, JobListing, Mentor,
    MentorRequest, ForumCategory, ForumPost, ForumReply,
    UserSuccessStory, AnalyticsEvent, UserCareerGoal,
    LearningGoal, LearningProgress, CareerPivotAnalysis
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'experience_level', 'location', 'profile_picture_preview']
    list_filter = ['experience_level', 'updated_at']
    search_fields = ['user__username', 'bio', 'location']
    
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;"/>', 
                obj.profile_picture.url
            )
        return "No image"
    profile_picture_preview.short_description = "Profile Picture"


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ['title', 'primary_category', 'average_salary_min', 'average_salary_max', 'job_growth_rate']
    list_filter = ['primary_category']
    search_fields = ['title', 'description']
    filter_horizontal = ['required_skills']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'detailed_description', 'primary_category', 'secondary_categories')
        }),
        ('Salary & Benefits', {
            'fields': ('average_salary_min', 'average_salary_max', 'job_growth_rate')
        }),
        ('Requirements', {
            'fields': ('required_education', 'certifications')
        }),
        ('Additional Info', {
            'fields': ('work_environment', 'typical_companies', 'average_rating', 'career_outlook')
        }),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'difficulty_level']
    list_filter = ['category', 'difficulty_level']
    search_fields = ['name', 'description']
    filter_horizontal = ['careers']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'difficulty_level')
        }),
        ('Learning Resources', {
            'fields': ('learning_resources', 'careers')
        }),
    )


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'proficiency_level', 'years_of_experience']
    list_filter = ['proficiency_level', 'acquired_at']
    search_fields = ['user__username', 'skill__name']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'top_category', 'completed_at', 'scores_summary']
    list_filter = ['top_category', 'completed_at', 'user']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['session_id', 'completed_at', 'scores']
    fieldsets = (
        ('User & Category', {
            'fields': ('user', 'top_category')
        }),
        ('Data', {
            'fields': ('session_id', 'scores', 'results', 'completed_at')
        }),
    )
    
    def get_user(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    get_user.short_description = 'User'
    
    def scores_summary(self, obj):
        if obj.scores:
            scores = obj.scores
            return f"R:{scores.get('Realistic',0)} I:{scores.get('Investigative',0)} A:{scores.get('Artistic',0)}"
        return "No scores"
    scores_summary.short_description = "RIASEC Scores"


@admin.register(CareerRoadmap)
class CareerRoadmapAdmin(admin.ModelAdmin):
    list_display = ['career', 'timeline_months', 'estimated_cost']
    list_filter = ['timeline_months']
    search_fields = ['career__title', 'steps', 'resources']
    fieldsets = (
        ('Career & Timeline', {
            'fields': ('career', 'timeline_months', 'estimated_cost')
        }),
        ('Content', {
            'fields': ('steps', 'resources', 'success_tips')
        }),
    )


@admin.register(CareerBookmark)
class CareerBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'career', 'bookmarked_at']
    list_filter = ['bookmarked_at']
    search_fields = ['user__username', 'career__title']


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'salary_min', 'posted_at']
    list_filter = ['posted_at', 'location', 'career']
    search_fields = ['title', 'company', 'description']
    filter_horizontal = ['required_skills']
    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'company', 'description', 'career')
        }),
        ('Location & Salary', {
            'fields': ('location', 'salary_min', 'salary_max')
        }),
        ('Requirements', {
            'fields': ('required_skills',)
        }),
        ('Metadata', {
            'fields': ('source', 'posted_at', 'expires_at', 'job_url')
        }),
    )


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'hourly_rate', 'is_verified', 'average_rating']
    list_filter = ['is_verified', 'specialization']
    search_fields = ['user__username', 'specialization__title', 'bio']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio')
        }),
        ('Expertise', {
            'fields': ('specialization', 'years_experience')
        }),
        ('Availability & Pricing', {
            'fields': ('availability', 'hourly_rate')
        }),
        ('Verification & Rating', {
            'fields': ('is_verified', 'average_rating')
        }),
    )


@admin.register(MentorRequest)
class MentorRequestAdmin(admin.ModelAdmin):
    list_display = ['mentee', 'mentor', 'status', 'requested_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['mentee__username', 'mentor__user__username']
    fieldsets = (
        ('Connection', {
            'fields': ('mentee', 'mentor')
        }),
        ('Communication', {
            'fields': ('message',)
        }),
        ('Scheduling', {
            'fields': ('scheduled_date',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )


@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'post_count']
    search_fields = ['name', 'description']
    
    def post_count(self, obj):
        return obj.forum_posts.count()
    post_count.short_description = "Number of Posts"


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'views', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['views', 'upvotes', 'created_at', 'updated_at']
    fieldsets = (
        ('Post Information', {
            'fields': ('author', 'category', 'career', 'title')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Engagement', {
            'fields': ('views', 'upvotes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'upvotes', 'is_solution', 'created_at']
    list_filter = ['is_solution', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['upvotes', 'created_at', 'updated_at']


@admin.register(UserSuccessStory)
class UserSuccessStoryAdmin(admin.ModelAdmin):
    list_display = ['author', 'career', 'featured', 'created_at']
    list_filter = ['featured', 'created_at', 'career']
    search_fields = ['author__username', 'story', 'career__title']
    fieldsets = (
        ('Author & Career', {
            'fields': ('author', 'career')
        }),
        ('Story Content', {
            'fields': ('title', 'story', 'current_role', 'years_in_career', 'challenges_faced', 'tips_for_others', 'image')
        }),
        ('Visibility', {
            'fields': ('featured',)
        }),
    )


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'get_user', 'timestamp', 'event_data']
    list_filter = ['event_type', 'timestamp', 'career']
    search_fields = ['user__username', 'event_type']
    readonly_fields = ['timestamp']
    
    def get_user(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    get_user.short_description = 'User'
    
    def event_data(self, obj):
        if obj.metadata:
            return str(obj.metadata)[:100]
        return "—"
    event_data.short_description = "Metadata"


@admin.register(UserCareerGoal)
class UserCareerGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_career', 'target_proficiency_level', 'target_timeline_months', 'updated_at']
    list_filter = ['target_proficiency_level', 'updated_at']
    search_fields = ['user__username', 'target_career__title']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Career Goal', {
            'fields': ('user', 'target_career')
        }),
        ('Target', {
            'fields': ('target_proficiency_level', 'target_timeline_months')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'target_proficiency', 'estimated_hours', 'completed']
    list_filter = ['completed', 'target_proficiency', 'created_at']
    search_fields = ['user__username', 'skill__name']
    readonly_fields = ['created_at']
    fieldsets = (
        ('User & Skill', {
            'fields': ('user', 'skill')
        }),
        ('Target', {
            'fields': ('target_proficiency', 'estimated_hours', 'deadline')
        }),
        ('Status', {
            'fields': ('completed',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ['learning_goal', 'hours_completed', 'completed_percentage', 'logged_at']
    list_filter = ['completed_percentage', 'logged_at']
    search_fields = ['learning_goal__user__username', 'learning_goal__skill__name']
    readonly_fields = ['logged_at']
    fieldsets = (
        ('Goal', {
            'fields': ('learning_goal',)
        }),
        ('Progress', {
            'fields': ('hours_completed', 'completed_percentage', 'milestone_reached')
        }),
        ('Courses', {
            'fields': ('courses_completed',)
        }),
        ('Timestamps', {
            'fields': ('logged_at',)
        }),
    )


@admin.register(CareerPivotAnalysis)
class CareerPivotAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_career_type', 'target_career', 'ai_generated', 'created_at']
    list_filter = ['ai_generated', 'created_at']
    search_fields = ['user__username', 'current_career_type', 'target_career__title']
    readonly_fields = ['created_at', 'analysis']
    fieldsets = (
        ('User & Career', {
            'fields': ('user', 'current_career_type', 'target_career')
        }),
        ('Analysis', {
            'fields': ('analysis',)
        }),
        ('Metadata', {
            'fields': ('ai_generated', 'created_at')
        }),
    )
