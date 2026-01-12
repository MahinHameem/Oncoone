"""Run Django migrations"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command

print("=" * 60)
print("Running makemigrations...")
print("=" * 60)
try:
    call_command('makemigrations')
    print("\n✓ makemigrations completed successfully!")
except Exception as e:
    print(f"\n✗ makemigrations failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Running migrate...")
print("=" * 60)
try:
    call_command('migrate')
    print("\n✓ migrate completed successfully!")
except Exception as e:
    print(f"\n✗ migrate failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All migrations completed successfully!")
print("=" * 60)
