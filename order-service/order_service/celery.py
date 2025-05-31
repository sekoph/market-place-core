
from celery import Celery
import os
import django
from django.conf import settings

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')

# Setup Django before importing models/tasks
django.setup()

app = Celery('order_service')

# Configure Celery using settings from Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed Django apps
app.autodiscover_tasks()

# Explicitly import your tasks to ensure they're registered
app.autodiscover_tasks(['order.utils'])