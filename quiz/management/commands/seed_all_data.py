import json
from django.core.management.base import BaseCommand
from django.db.models import Q
from quiz.models import Career, Skill, Assessment, User, UserProfile, CareerRoadmap


class Command(BaseCommand):
    help = 'Seed database with careers, skills, and sample assessments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))
        
        # Seed Skills
        self.seed_skills()
        self.stdout.write(self.style.SUCCESS('✓ Skills seeded'))
        
        # Seed Careers
        self.seed_careers()
        self.stdout.write(self.style.SUCCESS('✓ Careers seeded'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Data seeding completed!'))

    def seed_skills(self):
        """Create all skills if they don't exist"""
        skills_data = {
            'Technical': [
                {'name': 'Python', 'description': 'Python programming language'},
                {'name': 'JavaScript', 'description': 'JavaScript/Web development'},
                {'name': 'SQL', 'description': 'Database management'},
                {'name': 'Machine Learning', 'description': 'ML/AI algorithms'},
                {'name': 'Data Analysis', 'description': 'Data analytics and visualization'},
                {'name': 'Cloud Computing', 'description': 'AWS/GCP/Azure'},
                {'name': 'DevOps', 'description': 'CI/CD pipelines and infrastructure'},
            ],
            'Soft Skills': [
                {'name': 'Communication', 'description': 'Effective communication'},
                {'name': 'Leadership', 'description': 'Team leadership'},
                {'name': 'Problem Solving', 'description': 'Analytical problem solving'},
                {'name': 'Teamwork', 'description': 'Collaboration and teamwork'},
                {'name': 'Adaptability', 'description': 'Flexibility and adaptability'},
                {'name': 'Time Management', 'description': 'Efficient time management'},
                {'name': 'Critical Thinking', 'description': 'Critical thinking skills'},
            ],
            'Business': [
                {'name': 'Project Management', 'description': 'Project planning and execution'},
                {'name': 'Financial Analysis', 'description': 'Financial modeling and analysis'},
                {'name': 'Business Strategy', 'description': 'Strategic planning'},
                {'name': 'Marketing', 'description': 'Marketing and brand strategy'},
                {'name': 'Sales', 'description': 'Sales and business development'},
                {'name': 'Negotiation', 'description': 'Negotiation skills'},
            ],
            'Creative': [
                {'name': 'UI/UX Design', 'description': 'User interface and experience design'},
                {'name': 'Graphic Design', 'description': 'Visual design and graphics'},
                {'name': 'Content Writing', 'description': 'Content creation and copywriting'},
                {'name': 'Video Production', 'description': 'Video editing and production'},
                {'name': 'Creative Thinking', 'description': 'Innovation and creative ideation'},
            ],
        }
        
        for category, skills_list in skills_data.items():
            for skill_data in skills_list:
                Skill.objects.get_or_create(
                    name=skill_data['name'],
                    defaults={
                        'category': category,
                        'description': skill_data['description'],
                        'learning_resources': {
                            'courses': [
                                f"Udemy course on {skill_data['name']}",
                                f"Coursera specialization in {skill_data['name']}",
                            ],
                            'books': [f"Book on {skill_data['name']}"],
                            'tutorials': [f"Free tutorials on {skill_data['name']}"]
                        }
                    }
                )

    def seed_careers(self):
        """Create all careers with RIASEC mappings and required skills"""
        careers_data = [
            {
                'title': 'Software Developer',
                'description': 'Design and build applications and software systems',
                'primary_category': 'Investigative',
                'average_salary_min': 100000,
                'average_salary_max': 140000,
                'job_growth_rate': 15.0,
                'skills': ['Python', 'JavaScript', 'Problem Solving', 'Communication'],
                'roadmap': [
                    {'step': 1, 'title': 'Learn Fundamentals', 'duration_months': 3, 'description': 'Master programming basics'},
                    {'step': 2, 'title': 'Build Projects', 'duration_months': 6, 'description': 'Create portfolio projects'},
                    {'step': 3, 'title': 'Learn Frameworks', 'duration_months': 3, 'description': 'Master web frameworks'},
                    {'step': 4, 'title': 'Get Internship', 'duration_months': 6, 'description': 'First professional experience'},
                    {'step': 5, 'title': 'Senior Developer', 'duration_months': 24, 'description': 'Progress to senior role'},
                ]
            },
            {
                'title': 'Data Scientist',
                'description': 'Extract insights from data using statistical and ML techniques',
                'primary_category': 'Investigative',
                'average_salary_min': 110000,
                'average_salary_max': 150000,
                'job_growth_rate': 36.0,
                'skills': ['Python', 'Data Analysis', 'Machine Learning', 'SQL'],
                'roadmap': [
                    {'step': 1, 'title': 'Math & Stats Foundation', 'duration_months': 3, 'description': 'Strengthen math skills'},
                    {'step': 2, 'title': 'Learn Python & Libraries', 'duration_months': 3, 'description': 'Pandas, NumPy, Scikit-learn'},
                    {'step': 3, 'title': 'Build ML Models', 'duration_months': 6, 'description': 'Create predictive models'},
                    {'step': 4, 'title': 'Data Portfolio', 'duration_months': 6, 'description': 'Kaggle competitions and projects'},
                    {'step': 5, 'title': 'Senior Data Scientist', 'duration_months': 20, 'description': 'Lead DS initiatives'},
                ]
            },
            {
                'title': 'Product Manager',
                'description': 'Guide product strategy, roadmap, and execution',
                'primary_category': 'Enterprising',
                'average_salary_min': 110000,
                'average_salary_max': 140000,
                'job_growth_rate': 8.0,
                'skills': ['Leadership', 'Communication', 'Business Strategy', 'Project Management'],
                'roadmap': [
                    {'step': 1, 'title': 'Business Fundamentals', 'duration_months': 3, 'description': 'Learn product principles'},
                    {'step': 2, 'title': 'Associate PM Role', 'duration_months': 6, 'description': 'First PM position'},
                    {'step': 3, 'title': 'Product Strategy', 'duration_months': 6, 'description': 'Build strategic thinking'},
                    {'step': 4, 'title': 'Lead Product Team', 'duration_months': 12, 'description': 'Manage PM team'},
                    {'step': 5, 'title': 'Head of Product', 'duration_months': 24, 'description': 'Executive product role'},
                ]
            },
            {
                'title': 'DevOps Engineer',
                'description': 'Build infrastructure, automate deployment, ensure system reliability',
                'primary_category': 'Investigative',
                'average_salary_min': 120000,
                'average_salary_max': 160000,
                'job_growth_rate': 13.0,
                'skills': ['Cloud Computing', 'DevOps', 'Python', 'Problem Solving'],
                'roadmap': [
                    {'step': 1, 'title': 'Linux & Networking', 'duration_months': 2, 'description': 'OS and network basics'},
                    {'step': 2, 'title': 'Container Technology', 'duration_months': 3, 'description': 'Docker and Kubernetes'},
                    {'step': 3, 'title': 'Cloud Platforms', 'duration_months': 3, 'description': 'AWS/GCP/Azure'},
                    {'step': 4, 'title': 'CI/CD Pipelines', 'duration_months': 4, 'description': 'Jenkins, GitLab CI'},
                    {'step': 5, 'title': 'Senior DevOps', 'duration_months': 18, 'description': 'Infrastructure leadership'},
                ]
            },
            {
                'title': 'UX/UI Designer',
                'description': 'Create beautiful and intuitive user experiences',
                'primary_category': 'Artistic',
                'average_salary_min': 90000,
                'average_salary_max': 120000,
                'job_growth_rate': 11.0,
                'skills': ['UI/UX Design', 'Creative Thinking', 'Communication', 'Problem Solving'],
                'roadmap': [
                    {'step': 1, 'title': 'Design Fundamentals', 'duration_months': 2, 'description': 'Design principles and theory'},
                    {'step': 2, 'title': 'Design Tools', 'duration_months': 2, 'description': 'Figma, Adobe XD mastery'},
                    {'step': 3, 'title': 'Build Portfolio', 'duration_months': 6, 'description': 'Real-world design projects'},
                    {'step': 4, 'title': 'UX Research', 'duration_months': 3, 'description': 'User research and testing'},
                    {'step': 5, 'title': 'Design Leadership', 'duration_months': 20, 'description': 'Lead design team'},
                ]
            },
            {
                'title': 'Business Analyst',
                'description': 'Analyze business needs and drive data-informed decisions',
                'primary_category': 'Conventional',
                'average_salary_min': 75000,
                'average_salary_max': 100000,
                'job_growth_rate': 7.0,
                'skills': ['Business Strategy', 'Data Analysis', 'Communication', 'Project Management'],
                'roadmap': [
                    {'step': 1, 'title': 'Business Essentials', 'duration_months': 2, 'description': 'Business domain knowledge'},
                    {'step': 2, 'title': 'Analytics Tools', 'duration_months': 3, 'description': 'SQL, Tableau, Excel'},
                    {'step': 3, 'title': 'Stakeholder Management', 'duration_months': 6, 'description': 'Requirements gathering'},
                    {'step': 4, 'title': 'Strategic Analysis', 'duration_months': 6, 'description': 'Drive business strategy'},
                    {'step': 5, 'title': 'Senior BA/Manager', 'duration_months': 18, 'description': 'Management position'},
                ]
            },
            {
                'title': 'Machine Learning Engineer',
                'description': 'Build and deploy ML systems for production',
                'primary_category': 'Investigative',
                'average_salary_min': 130000,
                'average_salary_max': 180000,
                'job_growth_rate': 22.0,
                'skills': ['Machine Learning', 'Python', 'Cloud Computing', 'DevOps'],
                'roadmap': [
                    {'step': 1, 'title': 'ML Foundations', 'duration_months': 4, 'description': 'Algorithms and theory'},
                    {'step': 2, 'title': 'Deep Learning', 'duration_months': 3, 'description': 'Neural networks and TensorFlow'},
                    {'step': 3, 'title': 'Production ML', 'duration_months': 6, 'description': 'MLOps and deployment'},
                    {'step': 4, 'title': 'Specialize', 'duration_months': 6, 'description': 'NLP, CV, or RL specialization'},
                    {'step': 5, 'title': 'ML Leadership', 'duration_months': 18, 'description': 'Lead ML research/teams'},
                ]
            },
            {
                'title': 'Content Strategist',
                'description': 'Develop and execute content marketing strategies',
                'primary_category': 'Artistic',
                'average_salary_min': 60000,
                'average_salary_max': 85000,
                'job_growth_rate': 6.0,
                'skills': ['Content Writing', 'Marketing', 'Communication', 'Creative Thinking'],
                'roadmap': [
                    {'step': 1, 'title': 'Content Fundamentals', 'duration_months': 2, 'description': 'Writing and storytelling'},
                    {'step': 2, 'title': 'SEO Mastery', 'duration_months': 3, 'description': 'Search and content optimization'},
                    {'step': 3, 'title': 'Content Tools', 'duration_months': 2, 'description': 'CMS, analytics platforms'},
                    {'step': 4, 'title': 'Strategy Development', 'duration_months': 6, 'description': 'Content strategy creation'},
                    {'step': 5, 'title': 'Content Director', 'duration_months': 18, 'description': 'Lead content team'},
                ]
            },
        ]
        
        for career_data in careers_data:
            try:
                career, created = Career.objects.get_or_create(
                    title=career_data['title'],
                    defaults={
                        'description': career_data['description'],
                        'primary_category': career_data['primary_category'],
                        'average_salary_min': career_data.get('average_salary_min'),
                        'average_salary_max': career_data.get('average_salary_max'),
                        'job_growth_rate': career_data.get('job_growth_rate'),
                    }
                )
                
                # Add required skills to career
                for skill_name in career_data['skills']:
                    try:
                        skill = Skill.objects.get(name=skill_name)
                        career.required_skills.add(skill)
                    except Skill.DoesNotExist:
                        pass
                
                # Create roadmap if it doesn't exist
                if not hasattr(career, 'roadmap'):
                    CareerRoadmap.objects.get_or_create(
                        career=career,
                        defaults={
                            'steps': career_data.get('roadmap', []),
                            'timeline_months': 12,
                        }
                    )
            except Exception as e:
                self.stdout.write(f"Error creating career {career_data['title']}: {str(e)}")
