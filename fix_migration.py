import django
import os
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute(
    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
    ['core', '0003_5_cleanup_duplicate_emails', datetime.now()]
)
print("Migration record added successfully")
