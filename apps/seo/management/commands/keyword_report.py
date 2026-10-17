"""
docs/programmatic-seo-keywords.md dosyasını üretir: her pSEO sayfası × 16 dil → URL, H1, hedef keyword'ler.

  python manage.py keyword_report
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import translation

from dental_tourism.languages import LANGUAGE_META

from apps.seo import package_data as P
from apps.seo.management.commands.seed_topics import METRICS
from apps.seo.models import SeoTopic
from apps.seo.topics import NOT_TARGETED, PRICE_KEYWORDS, TOPICS, TREATMENT_PAGE_KEYWORDS
from apps.treatments.models import Treatment

OUT = Path(settings.BASE_DIR) / "docs" / "programmatic-seo-keywords.md"


def _kw(term):
    m = METRICS.get(term)
    if not m:
        return term
    vol, cpc, pd = m
    bits = [f"{vol:,} hacim" if vol else "", f"${cpc} CPC" if cpc else "", f"PD {pd}" if pd is not None else ""]
    return f"{term} *({', '.join(b for b in bits if b)})*"


class Command(BaseCommand):
    help = "Programatik SEO keyword → sayfa haritasını Markdown olarak yazar"

    def handle(self, **o):
        site = settings.SITE_URL
        L = []
        w = L.append
        w("# Programatik SEO — keyword → sayfa haritası\n")
        w("Otomatik üretilir: `python manage.py keyword_report`. Kaynaklar: `apps/seo/topics.py`, "
          "`apps/seo/package_data.py`, Keyword tablosu (admin → SEO → Keywords).\n")
        w("Kurallar: sayfalarda **fiyat rakamı yok** (\"oldukça uygun, telefon/WhatsApp'tan kişisel fiyat\"); "
          "her pSEO sayfasında gerçek klinik fotoğrafları, hekim/otorite kutusu, yorumlar ve "
          "ana sayfa · hakkımızda · yorumlar · Instagram · Google · drdevrim.com/<dil>/ · "
          "devrimbirikensipahi.com.tr/<dil>/ backlink'leri var. Hepsi sitemap'te, hreflang + x-default ile.\n")

        w("\n## 1. Konu (rehber) sayfaları — `/<dil>/<guide>/<slug>/`\n")
        for t in SeoTopic.objects.order_by("order"):
            data = TOPICS.get(t.key, {})
            w(f"\n### {t.key} — grup {t.group}\n")
            w("| Dil | URL | H1 | Keyword'ler |\n|---|---|---|---|")
            for lang in LANGUAGE_META:
                loc = t.localized(lang, fallback=False)
                if loc is None:
                    continue
                with translation.override(lang):
                    url = reverse("guides:detail", kwargs={"slug": loc.slug})
                kws = ", ".join(_kw(k) for k in data.get("keywords", {}).get(lang, []))
                w(f"| {lang} | {site}{url} | {loc.h1} | {kws} |")

        w("\n## 2. Fiyat sayfaları (rakamsız) — G2 / G3\n")
        w("| Dil | URL | Keyword'ler |\n|---|---|---|")
        for lang in LANGUAGE_META:
            with translation.override(lang):
                url = reverse("prices:index")
            w(f"| {lang} | {site}{url} | {', '.join(_kw(k) for k in PRICE_KEYWORDS['index'].get(lang, []))} |")
        w("\n**Tedavi fiyat sayfaları** (`/<dil>/<prices>/<tedavi-slug>/`, 10 tedavi × 16 dil). Her dilde kalıp: "
          "`" + "`, `".join(f"{lg}: {p}" for lg, p in PRICE_KEYWORDS["treatment_pattern"].items()) + "`\n")
        for slug, kws in PRICE_KEYWORDS["treatment"].items():
            w(f"- `{slug}` (EN ek): {', '.join(_kw(k) for k in kws)}")

        w("\n## 3. Paket sayfaları\n")
        w("| Dil | Hub URL | Keyword'ler |\n|---|---|---|")
        for lang in LANGUAGE_META:
            with translation.override(lang):
                url = reverse("packages:index")
            w(f"| {lang} | {site}{url} | {', '.join(_kw(k) for k in P.keywords_for(lang, 'hub'))} |")
        w("\n**Tedavi paketleri** `/<dil>/<packages>/<tedavi-slug>/` — kalıplar: " + "; ".join(
            f"{lg}: {', '.join(v.get('treatment', []))}" for lg, v in P.PACKAGE_KEYWORDS.items()))
        w("\nEk (EN, \"best … clinic in Istanbul\" bölümü):")
        for slug, kws in TREATMENT_PAGE_KEYWORDS.items():
            w(f"- `{slug}`: {', '.join(_kw(k) for k in kws)}")

        w("\n### Ülkeden paket sayfaları — `/<dil>/<dental-holidays-from>/<ülke>/`\n")
        w("| Dil | URL | Keyword'ler |\n|---|---|---|")
        for lang in LANGUAGE_META:
            for code in P.origin_codes(lang):
                with translation.override(lang):
                    url = reverse("origins:detail", kwargs={"country": P.country_slug(code, lang)})
                kws = P.keywords_for(lang, "origin", country=P.country_name(code, lang), cities=P.ORIGINS[code]["cities"])
                w(f"| {lang} | {site}{url} | {', '.join(kws)} |")

        from apps.seo import area_data as A

        w("\n### Semt sayfaları — `/<dil>/<dental-clinic>/<semt>/` (klinik Şişli'de; diğerleri \"near\")\n")
        w("Hub keyword'leri: " + "; ".join(f"{lg}: {', '.join(v)}" for lg, v in A.HUB_KEYWORDS.items()))
        w("\n| Dil | URL | Keyword'ler |\n|---|---|---|")
        for lang in LANGUAGE_META:
            for key in A.ordered_keys():
                with translation.override(lang):
                    url = reverse("areas:detail", kwargs={"area": key})
                w(f"| {lang} | {site}{url} | {', '.join(A.keywords_for(lang, key))} |")

        w("\n## 4. Tedavi sayfaları — `/<dil>/<treatments>/<slug>/` (16 dil)\n")
        w("| Tedavi | " + " | ".join(LANGUAGE_META) + " |\n|---|" + "---|" * len(LANGUAGE_META))
        for t in Treatment.objects.filter(is_active=True):
            cells = []
            for lang in LANGUAGE_META:
                loc = t.localized(lang, fallback=False)
                cells.append(loc.slug if loc else "—")
            w(f"| {t.slug} | " + " | ".join(cells) + " |")

        w("\n## 5. Bilinçli olarak HEDEFLENMEYENLER\n")
        for k, v in NOT_TARGETED.items():
            w(f"- **{k}**: {v}")
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"✓ {OUT} ({len(L)} satır)"))
