#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saarthi.settings')
django.setup()

from django.contrib.auth.models import User
from quiz.models import Assessment

# Get both users
shivansh = User.objects.get(username='Shivansh')
shivansph = User.objects.get(username='ShivanshPhadtare')

print(f"Before:")
print(f"  Shivansh: {shivansh.assessments.count()} assessments")
print(f"  ShivanshPhadtare: {shivansph.assessments.count()} assessments")

# Get the 3 newest assessments from ShivanshPhadtare
recent_3 = shivansph.assessments.all()[:3]

print(f"\nMoving {recent_3.count()} recent assessments from ShivanshPhadtare to Shivansh:")
for a in recent_3:
    print(f"  → {a.top_category} ({a.completed_at.strftime('%Y-%m-%d %H:%M')})")
    a.user = shivansh
    a.save()

print(f"\nAfter:")
print(f"  Shivansh: {shivansh.assessments.count()} assessments ✅")
print(f"  ShivanshPhadtare: {shivansph.assessments.count()} assessments")
