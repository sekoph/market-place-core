
# from celery import Celery
# import os
# import django
# from django.conf import settings

# # Set default Django settings
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')

# # Setup Django before importing models/tasks
# django.setup()

# app = Celery('order_service')

# # Configure Celery using settings from Django settings.py
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Auto-discover tasks from all installed Django apps
# app.autodiscover_tasks()

# # Explicitly import your tasks to ensure they're registered
# app.autodiscover_tasks(['order.utils'])


from celery import Celery
import os

# Set default Django settings but DON'T call django.setup() here
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')

app = Celery('order_service')

# This will be called when Celery worker actually starts
@app.on_after_configure.connect
def setup_django(sender, **kwargs):
    import django
    django.setup()

# Configure Celery using settings from Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed Django apps
app.autodiscover_tasks()

# Explicitly import your tasks to ensure they're registered
app.autodiscover_tasks(['order.utils'])