from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Hannes dev command"

    def handle(self, *args, **options):
        print("nothing to do")
