from django.core.management.base import BaseCommand
from django.utils import timezone

from store_data.models import Competitor
from store_data.competitors.essentra import load_essentra_products
from store_data.competitors.mocap import load_mocap_products

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        load_mocap_products()
        # self.stdout.write("It's now %s" % time)
        print("It's now %s" % time)