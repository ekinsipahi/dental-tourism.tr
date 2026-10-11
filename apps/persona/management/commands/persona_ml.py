from django.core.management.base import BaseCommand

from apps.persona import bandit
from apps.persona.models import MLModelVersion, PersonaExposure


class Command(BaseCommand):
    help = "Persona ML: train | status"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["train", "status", "simulate"])
        parser.add_argument("--visitors", type=int, default=3000)
        parser.add_argument("--keep", action="store_true", help="Simülasyon verisini veritabanında bırak")
        parser.add_argument("--force", action="store_true", help="Minimum veri eşiğini yok say")

    def handle(self, action, force=False, **o):
        if action == "simulate":
            import json

            from apps.persona.simulation import run

            self.stdout.write(f"Simülasyon: {o['visitors']} sanal ziyaretçi (gerçek motor üzerinden)…")
            result = run(n=o["visitors"], keep=o["keep"], log=self.stdout.write)
            self.stdout.write(json.dumps(result, indent=2, default=str))
            return
        if action == "train":
            from apps.persona.ml import train

            result = train(force=force)
            style = self.style.SUCCESS if result.get("trained") else self.style.WARNING
            self.stdout.write(style(str(result)))
            return
        n = PersonaExposure.objects.count()
        c = PersonaExposure.objects.filter(converted=True).count()
        self.stdout.write(self.style.SUCCESS(f"Exposures: {n}  Conversions: {c}"))
        self.stdout.write(f"{'arm':10} {'imp':>7} {'conv':>6} {'CR%':>6} {'P(best)%':>9}")
        for a in bandit.summary():
            self.stdout.write(f"{a['persona']:10} {a['impressions']:>7} {a['conversions']:>6} "
                              f"{a['rate']:>6} {a['p_best']:>9}")
        active = MLModelVersion.objects.filter(is_active=True).first()
        self.stdout.write(f"Active ML model: {active or '— (bandit policy in use)'}")
