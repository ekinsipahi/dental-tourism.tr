"""
AI içerik üretimi (Claude):

  python manage.py content generate-treatments [--overwrite]      tedavi sayfası gövdeleri (kaynak dil)
  python manage.py content generate-landing [--overwrite]         programatik sayfa metinleri
  python manage.py content generate-post --topic "..." --lang de [--treatment dental-implants] [--funnel decision]
  python manage.py content from-keywords --lang de --limit 5      sayfası olmayan blog keyword'lerinden taslak
  python manage.py content related                                 ilgili yazıları hesapla (TF-IDF)

Üretilen içerik kaydedilince diğer 15 dile otomatik çevrilir (yayınlanan blog yazıları için).
"""
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Claude ile SEO içerik üretimi"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["generate-treatments", "generate-landing", "generate-post",
                                               "from-keywords", "related"])
        parser.add_argument("--topic", default="")
        parser.add_argument("--lang", default="en")
        parser.add_argument("--treatment", default="")
        parser.add_argument("--funnel", default="awareness", choices=["awareness", "consideration", "decision"])
        parser.add_argument("--limit", type=int, default=5)
        parser.add_argument("--overwrite", action="store_true")

    def handle(self, action, **o):
        from apps.localization.llm import is_configured

        if action != "related" and not is_configured():
            raise CommandError("ANTHROPIC_API_KEY .env içinde tanımlı değil.")
        from apps.blog.content_machine import ContentMachine

        m = ContentMachine()
        if action == "generate-treatments":
            from apps.treatments.models import Treatment

            for t in Treatment.objects.filter(is_active=True):
                if len((t.body or "").split()) > 500 and not o["overwrite"]:
                    self.stdout.write(f"  ⏭ {t.name} (zaten içerik var)")
                    continue
                m.generate_treatment_content(t, overwrite=True)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {t.name}"))
        elif action == "generate-landing":
            from apps.seo.models import LandingPage

            for p in LandingPage.objects.filter(is_active=True).select_related("treatment", "city"):
                if p.generated_by_ai and not o["overwrite"]:
                    continue
                m.generate_landing(p, overwrite=True)
                p.noindex = False
                p.save(update_fields=["noindex"])
                self.stdout.write(self.style.SUCCESS(f"  ✓ {p}"))
        elif action == "generate-post":
            from apps.treatments.models import Treatment

            if not o["topic"]:
                raise CommandError("--topic gerekli")
            t = Treatment.objects.filter(key=o["treatment"]).first() if o["treatment"] else None
            post = m.generate_post(o["topic"], lang=o["lang"], funnel_stage=o["funnel"], treatment=t)
            self.stdout.write(self.style.SUCCESS(f"✓ Taslak #{post.pk}: {post.title} (status=review — admin'den "
                                                 "kontrol edip yayınlayın; yayınlanınca 15 dile çevrilir)"))
        elif action == "from-keywords":
            from apps.seo.models import Keyword

            kws = (Keyword.objects.filter(language=o["lang"], page_type="blog", blog_post__isnull=True)
                   .exclude(status="ignored").order_by("-priority", "-search_volume")[: o["limit"]])
            for kw in kws:
                post = m.generate_post_from_keyword(kw)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {kw.term} → #{post.pk if post else '—'}"))
        elif action == "related":
            from apps.blog.tasks import compute_related_posts

            self.stdout.write(str(compute_related_posts()))
