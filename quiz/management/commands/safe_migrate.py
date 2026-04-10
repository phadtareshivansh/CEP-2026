"""
Management command to safely run migrations on Vercel
This is safe to run even if migrations have already been applied
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Safely run migrations with error handling for Vercel deployments'

    def handle(self, *args, **options):
        """
        Attempt to run migrations.
        If database is unavailable, gracefully skip.
        """
        try:
            # Test database connection
            connection = connections['default']
            connection.ensure_connection()
            
            self.stdout.write(
                self.style.SUCCESS('✓ Database connection successful')
            )
            
            # Run migrations
            self.stdout.write('Running migrations...')
            call_command('migrate', '--noinput')
            
            self.stdout.write(
                self.style.SUCCESS('✓ Migrations completed successfully')
            )
            
        except OperationalError as e:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠ Database not available: {str(e)}\n'
                    'Migrations will be retried on next deployment.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error running migrations: {str(e)}')
            )
            raise
