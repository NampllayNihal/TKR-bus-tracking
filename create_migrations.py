#!/usr/bin/env python
"""
Script to generate migrations for new apps without circular dependency issues.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'busproject.settings')
django.setup()

from django.core.management import call_command

# Create migrations for each app
apps_to_migrate = ['transport', 'users', 'payments', 'tracking']

for app in apps_to_migrate:
    print(f"\n{'='*60}")
    print(f"Creating migrations for: {app}")
    print(f"{'='*60}")
    try:
        call_command('makemigrations', app, verbosity=2, interactive=False)
        print(f"[OK] {app} migrations created successfully")
    except Exception as e:
        print(f"[ERROR] Error creating {app} migrations:")
        print(str(e))
        sys.exit(1)

print("\n[OK] All migrations created successfully!")


