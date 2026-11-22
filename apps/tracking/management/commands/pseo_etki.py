"""
pseo_etki — kardeş sitelerdeki pSEO budamasının (22.11.2026) ve dil genişlemesinin etkisini izleyen SALT-OKUNUR rapor.

    manage.py pseo_etki                   # son 7 gün ile önceki 7 gün, drd + dbs
    manage.py pseo_etki --days 14 --site drd

İnsan oturumu = HUMAN_Q (en az bir sayfa görüntülemiş, bot işareti yok). Komut hiçbir şey yazmaz.
Kaldırılan ilçe ve yazı listeleri kardeş depolardaki kaynak dosyaların kopyasıdır:
drdevrim app/data/istanbul-data-kaldirilan.ts, dbs blog/removed.py.
"""
from collections import Counter
from datetime import timedelta
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone

from apps.tracking.models import HUMAN_Q, VisitorSession

TR_FAMILIES = {"disci", "haftasonu", "en-iyi-disci", "uzman-dis-hekimi", "prof-dis-hekimi", "estetik-dis-klinigi"}
LANG_FAMILIES = {"en": "dentist", "ru": "stomatolog", "uk": "stomatolog", "bg": "zabolekar", "de": "zahnarzt",
                 "nl": "tandarts", "fr": "dentiste", "it": "dentista", "es": "dentista", "pl": "dentysta",
                 "ar": "tabib-asnan", "sv": "tandlakare", "da": "tandlaege", "no": "tannlege", "ro": "dentist",
                 "az": "dis-hekimi"}
REMOVED_DISTRICTS = {"adalar", "arnavutkoy", "atasehir", "avcilar", "basaksehir", "beykoz", "beylikduzu", "buyukcekmece",
                     "catalca", "cekmekoy", "esenyurt", "kartal", "kucukcekmece", "maltepe", "pendik", "sancaktepe",
                     "sile", "silivri", "sultangazi", "tuzla", "umraniye"}
REMOVED_DBS_POSTS = {"pendik-acik-disci", "kartal-acik-disci", "maltepe-acik-disci", "buyukcekmece-acik-disci",
                     "avcilar-acik-disci", "atasehir-acik-disci", "basaksehir-acik-disci", "kucukcekmece-acik-disci",
                     "umraniye-acik-disci", "beykoz-acik-disci", "anadolu-yakasi-acik-disci",
                     "acil-disci-istanbul", "ramazanda-acik-disci"}


def parse_landing(landing):
    """(aile, ilçe, mahalle) — pSEO dışı inişlerde aile = ilk yol parçası ('home' kök için)."""
    path = urlparse(landing).path if "://" in (landing or "") else (landing or "").split("?")[0]
    seg = [s for s in path.split("/") if s]
    if not seg:
        return "home", None, None
    if seg[0] in TR_FAMILIES:
        return seg[0], (seg[1] if len(seg) > 1 else None), (seg[2] if len(seg) > 2 else None)
    if seg[0] in LANG_FAMILIES and len(seg) > 1 and seg[1] == LANG_FAMILIES[seg[0]]:
        return f"{seg[0]}/{seg[1]}", (seg[2] if len(seg) > 2 else None), (seg[3] if len(seg) > 3 else None)
    return "/".join(seg[:3]), None, None


class Command(BaseCommand):
    help = "pSEO budaması / dil genişlemesi etki raporu (salt-okunur)"

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7, help="Pencere uzunluğu (gün); önceki eşit pencereyle karşılaştırılır")
        parser.add_argument("--site", default="all", help="drd, dbs veya all")
        parser.add_argument("--top", type=int, default=12)

    def handle(self, *args, **opts):
        days, top = opts["days"], opts["top"]
        sites = ["drd", "dbs"] if opts["site"] == "all" else [opts["site"]]
        now = timezone.now()
        windows = [("son %d gün" % days, now - timedelta(days=days), now),
                   ("önceki %d gün" % days, now - timedelta(days=2 * days), now - timedelta(days=days))]
        for site in sites:
            self.stdout.write(self.style.MIGRATE_HEADING(f"\n===== site={site} ====="))
            for label, start, end in windows:
                self.report(site, label, start, end, top)

    def report(self, site, label, start, end, top):
        qs = VisitorSession.objects.filter(site=site, created_at__gte=start, created_at__lt=end)
        human = qs.filter(HUMAN_Q)
        total, n_human = qs.count(), human.count()
        agg = human.aggregate(wa=Sum("whatsapp_clicks"), tel=Sum("phone_clicks"), form=Sum("form_submits"))
        contact_sessions = human.filter(whatsapp_clicks__gt=0).count() + human.filter(whatsapp_clicks=0, phone_clicks__gt=0).count() \
            + human.filter(whatsapp_clicks=0, phone_clicks=0, form_submits__gt=0).count()
        fam, ilce, ilce_contact, removed_hits, paths = Counter(), Counter(), Counter(), 0, Counter()
        for s in human.values("landing_page", "whatsapp_clicks", "phone_clicks", "form_submits"):
            f, i, _m = parse_landing(s["landing_page"])
            fam[f] += 1
            contact = bool(s["whatsapp_clicks"] or s["phone_clicks"] or s["form_submits"])
            if i:
                ilce[i] += 1
                if contact:
                    ilce_contact[i] += 1
                if i in REMOVED_DISTRICTS:
                    removed_hits += 1
            else:
                paths[f] += 1
                slug = (s["landing_page"] or "").rstrip("/").rsplit("/", 1)[-1]
                if slug in REMOVED_DBS_POSTS:
                    removed_hits += 1
        w = self.stdout.write
        w(f"\n--- {label}  ({start:%d.%m} → {end:%d.%m})")
        w(f"oturum: toplam={total} insan={n_human} bot={total - n_human}")
        w(f"iletişim (insan): oturum={contact_sessions} whatsapp={agg['wa'] or 0} telefon={agg['tel'] or 0} form={agg['form'] or 0}")
        w(f"kaldırılan sayfalara insan inişi: {removed_hits}  (dağıtımdan sonra 0'a inmeli)")
        w("insan inişi, aile: " + ", ".join(f"{k}={v}" for k, v in fam.most_common(top)))
        if ilce:
            w("insan inişi, ilçe (iletişim): " + ", ".join(
                f"{k}{'[KALDIRILDI]' if k in REMOVED_DISTRICTS else ''}={v}({ilce_contact[k]})" for k, v in ilce.most_common(top)))
        if paths and site != "drd":
            w("insan inişi, sayfa: " + ", ".join(f"{k}={v}" for k, v in paths.most_common(top)))
