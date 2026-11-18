"""
Persona kanıtını ham takip verisinden yeniden kurar.

  manage.py rebuild_personas --days 30                 # son 30 günün tüm insan oturumları
  manage.py rebuild_personas --days 30 --only-missing  # yalnızca iletişim tıklaması kanıta girmemiş olanlar
  manage.py rebuild_personas --site drd --limit 50
"""
from django.core.management.base import BaseCommand

from apps.persona.rebuild import rebuild_many


class Command(BaseCommand):
    help = "Persona kanıtını PageView + TrackingEvent satırlarından yeniden kurar (eşzamanlı yazma kayıplarını onarır)"

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30)
        parser.add_argument("--site", default="")
        parser.add_argument("--only-missing", action="store_true")
        parser.add_argument("--limit", type=int, default=None)

    def handle(self, *args, **o):
        stats = rebuild_many(days=o["days"], site=o["site"], only_missing=o["only_missing"], limit=o["limit"],
                             log=lambda s: self.stdout.write(s))
        self.stdout.write(self.style.SUCCESS(str(stats)))
