from django.core.management.base import BaseCommand
from django.utils import timezone

from store_data.models import Competitor
from store_data.competitors.essentra import store_essentra_products

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        store_essentra_products()
        self.stdout.write("It's now %s" % time)