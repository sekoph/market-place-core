from django.core.management.base import BaseCommand
from order.utils.event_handler import start_event_listener

class Command(BaseCommand):
    help = 'Start event consumer'

    def handle(self, *args, **options):
        self.stdout.write('Starting event listener...')
        start_event_listener()