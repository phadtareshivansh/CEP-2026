"""
Django management command to seed forum categories.
Usage: python manage.py seed_forum_categories
"""

from django.core.management.base import BaseCommand
from quiz.models import ForumCategory


class Command(BaseCommand):
    help = 'Seed default forum categories'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Career Guidance',
                'description': 'Get advice on career paths, transitions, and growth',
                'icon': '🚀'
            },
            {
                'name': 'Skill Development',
                'description': 'Discuss learning resources, courses, and skill-building tips',
                'icon': '💡'
            },
            {
                'name': 'Job Search & Interviews',
                'description': 'Share interview experiences and job hunting strategies',
                'icon': '💼'
            },
            {
                'name': 'Mentorship & Networking',
                'description': 'Connect with mentors and build professional relationships',
                'icon': '🤝'
            },
            {
                'name': 'Industry Insights',
                'description': 'Discuss industry trends, news, and market opportunities',
                'icon': '📊'
            },
            {
                'name': 'Success Stories',
                'description': 'Share and celebrate career success and achievements',
                'icon': '⭐'
            },
            {
                'name': 'Questions & Answers',
                'description': 'General Q&A about careers and skill development',
                'icon': '❓'
            },
            {
                'name': 'Introductions',
                'description': 'Introduce yourself and connect with the community',
                'icon': '👋'
            },
        ]

        created_count = 0
        for category_data in categories:
            category, created = ForumCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon'],
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created category: {category.name}'
                    )
                )
                created_count += 1
            else:
                self.stdout.write(
                    f'  Category already exists: {category.name}'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Forum categories setup complete! {created_count} new categories created.'
            )
        )
