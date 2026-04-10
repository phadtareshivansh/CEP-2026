#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saarthi.settings')
django.setup()

from django.contrib.auth.models import User
from quiz.models import Assessment

# Get total assessments
total_assessments = Assessment.objects.count()
print(f"📊 Total assessments in database: {total_assessments}")

# Check unassigned
unassigned = Assessment.objects.filter(user__isnull=True).count()
print(f"👻 Unassigned assessments (user=NULL): {unassigned}")

# List all users and their counts
print("\n📋 Assessment count by user:")
for user in User.objects.all():
    count = user.assessments.count()
    print(f"   → {user.username}: {count} assessments")

# Show top category for each assessment
print("\n📈 All assessments detail:")
for i, a in enumerate(Assessment.objects.all(), 1):
    user_name = a.user.username if a.user else "NULL"
    print(f"   {i}. {a.top_category} - User: {user_name} ({a.completed_at.strftime('%Y-%m-%d %H:%M')})")
