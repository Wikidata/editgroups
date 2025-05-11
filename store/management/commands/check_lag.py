from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from store.models import Edit


class Command(BaseCommand):
    MAX_SECONDS = 3000
    help = f"Exits with 1 if current lag is bigger than {MAX_SECONDS} seconds"

    def handle(self, *args, **options):
        lag = Edit.current_lag().total_seconds()
        print(f"Current lag: {lag:.2f} seconds")
        if lag > 3000:
            raise CommandError(f"Current lag is bigger than {self.MAX_SECONDS}")
