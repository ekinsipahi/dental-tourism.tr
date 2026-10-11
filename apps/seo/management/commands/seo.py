"""
SEO komutları:

  python manage.py seo keywords-seed [--lang de,nl]
  python manage.py seo keywords-expand --lang de [--treatment dental-implants] [--count 40]
  python manage.py seo keywords-import ahrefs_de.csv --lang de
  python manage.py seo keywords-assign
  python manage.py seo report [--lang de]
  python manage.py seo audit [--lang de]
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Sum

from apps.seo.models import Keyword


class Command(BaseCommand):
    help = "Keyword araştırması, eşleme ve on-page SEO denetimi"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["keywords-seed", "keywords-expand", "keywords-import",
                                               "keywords-assign", "report", "audit"])
        parser.add_argument("path", nargs="?")
        parser.add_argument("--lang", default="")
        parser.add_argument("--treatment", default="")
        parser.add_argument("--count", type=int, default=40)

    def handle(self, action, path=None, lang="", treatment="", count=40, **o):
        langs = [x.strip() for x in lang.split(",") if x.strip()] or None
        getattr(self, "_" + action.replace("-", "_"))(langs=langs, path=path, treatment=treatment, count=count)

    def _keywords_seed(self, langs, **_):
        from apps.seo.services import seed_keywords

        n = seed_keywords(langs)
        self.stdout.write(self.style.SUCCESS(f"✓ {n} yeni keyword"))

    def _keywords_expand(self, langs, treatment, count, **_):
        from apps.blog.content_machine import ContentMachine
        from apps.treatments.models import Treatment

        if not langs:
            raise CommandError("--lang gerekli")
        t = Treatment.objects.filter(key=treatment).first() if treatment else None
        machine = ContentMachine()
        for lg in langs:
            items = machine.expand_keywords(lg, t, count)
            created = 0
            for it in items:
                _, c = Keyword.objects.get_or_create(term=it["term"].strip().lower(), language=lg, defaults={
                    "treatment": t, "intent": it["intent"], "funnel_stage": it["funnel_stage"],
                    "persona_hint": it["persona_hint"], "page_type": it["page_type"],
                    "priority": max(1, min(100, it["priority"])), "source": "ai"})
                created += c
            self.stdout.write(self.style.SUCCESS(f"✓ [{lg}] {created} yeni keyword (AI)"))

    def _keywords_import(self, langs, path, **_):
        from apps.seo.services import import_csv

        if not path or not langs or len(langs) != 1:
            raise CommandError("Kullanım: seo keywords-import dosya.csv --lang de")
        created, updated = import_csv(path, langs[0])
        self.stdout.write(self.style.SUCCESS(f"✓ {created} yeni, {updated} güncellendi"))

    def _keywords_assign(self, **_):
        from apps.seo.services import assign_targets

        self.stdout.write(self.style.SUCCESS(f"✓ {assign_targets()} keyword hedef sayfaya bağlandı"))

    def _report(self, langs, **_):
        qs = Keyword.objects.all()
        if langs:
            qs = qs.filter(language__in=langs)
        self.stdout.write(f"{'lang':5} {'total':>6} {'targeted':>9} {'no target':>10} {'volume':>9}")
        for row in qs.values("language").annotate(n=Count("id"), vol=Sum("search_volume")).order_by("language"):
            lq = qs.filter(language=row["language"])
            self.stdout.write(f"{row['language']:5} {row['n']:>6} {lq.exclude(target_url='').count():>9} "
                              f"{lq.filter(target_url='').count():>10} {row['vol'] or 0:>9}")
        self.stdout.write("\nEn yüksek fırsatlı, sayfası olmayan kelimeler:")
        for kw in qs.filter(target_url="").exclude(status="ignored").order_by("-search_volume", "-priority")[:20]:
            self.stdout.write(f"  [{kw.language}] {kw.term}  vol={kw.search_volume or '-'}  → {kw.page_type}")

    def _audit(self, langs, **_):
        from apps.blog.models import BlogPost
        from apps.seo.audit import audit_landing, audit_post, audit_treatment
        from apps.seo.models import LandingPage
        from apps.treatments.models import Treatment

        langs = langs or [c for c, _ in settings.LANGUAGES]
        total = 0
        for lg in langs:
            rows = []
            for t in Treatment.objects.filter(is_active=True):
                if t.has_language(lg):
                    rows += [(f"treatment:{t.key}", i) for i in audit_treatment(t, lg)]
            for p in LandingPage.objects.filter(is_active=True, noindex=False):
                if p.has_language(lg):
                    rows += [(f"landing:{p.pk}", i) for i in audit_landing(p, lg)]
            for post in BlogPost.published.all():
                if post.has_language(lg):
                    rows += [(f"post:{post.pk}", i) for i in audit_post(post, lg)]
            if rows:
                self.stdout.write(self.style.WARNING(f"\n[{lg}] {len(rows)} sorun"))
                for ref, issue in rows:
                    self.stdout.write(f"  {ref:28} {issue}")
            total += len(rows)
        self.stdout.write(self.style.SUCCESS(f"\nToplam {total} sorun."))
