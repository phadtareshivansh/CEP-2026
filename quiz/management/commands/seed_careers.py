from django.core.management.base import BaseCommand
from quiz.models import Career, Skill

class Command(BaseCommand):
    help = 'Seed initial career and skill data'

    def handle(self, *args, **options):
        careers_data = [
            {
                'title': 'Data Scientist',
                'primary_category': 'Investigative',
                'description': 'Analyze data and find meaningful patterns',
                'detailed_description': 'Data scientists combine statistics, programming, and domain expertise to extract insights from data.',
                'average_salary_min': 80000,
                'average_salary_max': 150000,
                'job_growth_rate': 15.0,
                'required_education': 'Bachelor\'s in Computer Science, Statistics, or related field',
                'typical_companies': ['Google', 'Amazon', 'Microsoft', 'Apple', 'Facebook'],
                'work_environment': 'Office and remote work with focus on data analysis and visualization',
            },
            {
                'title': 'Software Engineer',
                'primary_category': 'Investigative',
                'description': 'Develop and maintain software applications',
                'detailed_description': 'Software engineers design, develop, and test software systems for various platforms.',
                'average_salary_min': 90000,
                'average_salary_max': 180000,
                'job_growth_rate': 22.0,
                'required_education': 'Bachelor\'s in Computer Science or Software Engineering',
                'typical_companies': ['Google', 'Microsoft', 'Apple', 'Amazon', 'Meta'],
                'work_environment': 'Office/remote with collaborative team environment',
            },
            {
                'title': 'UI/UX Designer',
                'primary_category': 'Artistic',
                'description': 'Create beautiful and intuitive user experiences',
                'detailed_description': 'UI/UX designers focus on creating user-friendly and visually appealing digital products.',
                'average_salary_min': 70000,
                'average_salary_max': 130000,
                'job_growth_rate': 13.0,
                'required_education': 'Bachelor\'s in Design, HCI, or related field',
                'typical_companies': ['Adobe', 'Google', 'Apple', 'Figma', 'InVision'],
                'work_environment': 'Creative office environment with design tools and collaboration',
            },
            {
                'title': 'Business Manager',
                'primary_category': 'Enterprising',
                'description': 'Lead teams and drive business growth',
                'detailed_description': 'Business managers oversee operations, manage teams, and ensure organizational objectives are met.',
                'average_salary_min': 75000,
                'average_salary_max': 160000,
                'job_growth_rate': 8.0,
                'required_education': 'Master\'s in Business Administration (MBA) preferred',
                'typical_companies': ['Fortune 500 companies', 'Tech startups', 'Consulting firms'],
                'work_environment': 'Corporate office with leadership responsibilities',
            },
            {
                'title': 'Therapist/Counselor',
                'primary_category': 'Social',
                'description': 'Help people overcome challenges and improve mental health',
                'detailed_description': 'Therapists provide mental health support through various therapeutic approaches.',
                'average_salary_min': 50000,
                'average_salary_max': 100000,
                'job_growth_rate': 12.0,
                'required_education': 'Master\'s in Psychology, Counseling, or Social Work',
                'typical_companies': ['Hospitals', 'Private practice', 'Mental health clinics'],
                'work_environment': 'Private offices or healthcare facilities',
            },
            {
                'title': 'Civil Engineer',
                'primary_category': 'Realistic',
                'description': 'Design and build infrastructure projects',
                'detailed_description': 'Civil engineers plan and oversee construction of buildings, roads, bridges, and other structures.',
                'average_salary_min': 65000,
                'average_salary_max': 140000,
                'job_growth_rate': 6.0,
                'required_education': 'Bachelor\'s in Civil Engineering',
                'typical_companies': ['Construction companies', 'Government agencies', 'Engineering firms'],
                'work_environment': 'Construction sites and design offices',
            },
            {
                'title': 'Accountant',
                'primary_category': 'Conventional',
                'description': 'Manage finances and ensure accuracy in financial records',
                'detailed_description': 'Accountants prepare and examine financial records to ensure accuracy and compliance.',
                'average_salary_min': 60000,
                'average_salary_max': 120000,
                'job_growth_rate': 5.0,
                'required_education': 'Bachelor\'s in Accounting',
                'typical_companies': ['Accounting firms', 'Corporations', 'Government agencies'],
                'work_environment': 'Office environment with detailed analytical work',
            },
            {
                'title': 'Marketing Manager',
                'primary_category': 'Enterprising',
                'description': 'Develop and execute marketing strategies',
                'detailed_description': 'Marketing managers create campaigns and strategies to promote products and services.',
                'average_salary_min': 65000,
                'average_salary_max': 135000,
                'job_growth_rate': 8.0,
                'required_education': 'Bachelor\'s in Marketing or Business',
                'typical_companies': ['Tech companies', 'Consumer brands', 'Agencies'],
                'work_environment': 'Corporate office with creative and analytical work',
            },
        ]

        # Create Skills
        skills_data = [
            {'name': 'Python', 'category': 'Technical'},
            {'name': 'JavaScript', 'category': 'Technical'},
            {'name': 'Data Analysis', 'category': 'Technical'},
            {'name': 'Machine Learning', 'category': 'Technical'},
            {'name': 'UI Design', 'category': 'Creative'},
            {'name': 'User Research', 'category': 'Soft Skills'},
            {'name': 'Leadership', 'category': 'Soft Skills'},
            {'name': 'Communication', 'category': 'Soft Skills'},
            {'name': 'Project Management', 'category': 'Soft Skills'},
            {'name': 'Excel', 'category': 'Technical'},
        ]

        created_skills = {}
        for skill_data in skills_data:
            try:
                skill, created = Skill.objects.get_or_create(**skill_data)
                created_skills[skill.name] = skill
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created skill: {skill.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating skill {skill_data.get("name")}: {e}'))

        # Create Careers
        for career_data in careers_data:
            try:
                career, created = Career.objects.get_or_create(
                    title=career_data['title'],
                    defaults={k: v for k, v in career_data.items() if k != 'title'}
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created career: {career.title}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Career already exists: {career.title}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating career {career_data.get("title")}: {e}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with career and skill data'))
