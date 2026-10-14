"""
İçerik çevirisi (Claude) — senkron, ilerlemeyi göstererek.

  python manage.py translate_content --missing                 # tüm modeller, eksik/eskimiş diller
  python manage.py translate_content --model blog.blogpost --lang de,nl
  python manage.py translate_content --model treatments.treatment --force
  python manage.py translate_content --status                  # kapsama raporu
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.localization import llm
from apps.localization.models import LIVE_STATUSES
from apps.localization.registry import all_specs, get_spec_by_label
from apps.localization.service import languages_needing_work, translate_object


class Command(BaseCommand):
    help = "Kayıtlı tüm içerik modellerini AI ile 17 dile çevirir"

    def add_arguments(self, parser):
        parser.add_argument("--model", default="", help="app_label.model (örn. blog.blogpost)")
        parser.add_argument("--lang", default="", help="virgülle ayrılmış dil kodları")
        parser.add_argument("--missing", action="store_true", help="sadece eksik/eskimiş/başarısız")
        parser.add_argument("--force", action="store_true", help="insan onaylılar hariç hepsini yeniden çevir")
        parser.add_argument("--status", action="store_true", help="sadece kapsama raporu")
        parser.add_argument("--id", type=int, default=None)

    def handle(self, model="", lang="", missing=False, force=False, status=False, id=None, **o):
        specs = {model.lower(): get_spec_by_label(model)} if model else all_specs()
        if model and specs[model.lower()] is None:
            raise CommandError(f"Bilinmeyen model: {model}. Seçenekler: {', '.join(all_specs())}")
        langs = [x.strip() for x in lang.split(",") if x.strip()]

        if status:
            return self._status(specs)
        if not llm.is_configured():
            raise CommandError("ANTHROPIC_API_KEY .env içinde tanımlı değil.")

        totals = {}
        for label, spec in specs.items():
            qs = spec.model.objects.all()
            if id:
                qs = qs.filter(pk=id)
            for obj in qs:
                if not force and not spec.should_auto_translate(obj):
                    continue
                todo = spec.target_languages(obj) if force else languages_needing_work(obj)
                if langs:
                    todo = [lg for lg in todo if lg in langs]
                for lg in todo:
                    result = translate_object(obj, lg, force=force)
                    totals[result] = totals.get(result, 0) + 1
                    mark = {"translated": "✓", "failed": "✗", "outdated": "⚠"}.get(result, "·")
                    self.stdout.write(f"  {mark} {label}#{obj.pk} [{lg}] {result}")
        self.stdout.write(self.style.SUCCESS(f"Bitti: {totals}"))

    def _status(self, specs):
        langs = [c for c, _ in settings.LANGUAGES]
        self.stdout.write(f"{'model':28} {'obj':>4}  " + " ".join(f"{c:>3}" for c in langs))
        for label, spec in specs.items():
            objs = list(spec.model.objects.all())
            counts = {c: 0 for c in langs}
            for obj in objs:
                live = set(obj.translations.filter(status__in=LIVE_STATUSES).values_list("language_code", flat=True))
                live.add(obj.source_language)
                for c in live:
                    counts[c] = counts.get(c, 0) + 1
            self.stdout.write(f"{label:28} {len(objs):>4}  " + " ".join(f"{counts[c]:>3}" for c in langs))
