#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# sys.path.append('/app')



def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer_service.settings')
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    shared_dir = os.path.join(parent_dir, 'shared')
    
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    if shared_dir not in sys.path:
        sys.path.insert(0, shared_dir)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
