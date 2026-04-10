#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saarthi.settings')
django.setup()

from django.contrib.auth.models import User
from quiz.models import Assessment

# Get the first user (or you can change this to your username)
user = User.objects.first()

if not user:
    print("❌ No users found in database!")
    exit(1)

print(f"📌 Assigning assessments to: {user.username}")

# Find all assessments with NO user assigned
unassigned = Assessment.objects.filter(user__isnull=True)
print(f"Found {unassigned.count()} assessments with no user")

# Assign them to the user
updated_count = unassigned.update(user=user)
print(f"✅ Updated {updated_count} assessments")

# Show summary
total = user.assessments.count()
print(f"\n📊 {user.username} now has {total} total assessments")
