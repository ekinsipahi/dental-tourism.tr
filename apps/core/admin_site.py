"""
Özel admin paneli — dentaltourism.tr yönetimi.

  /admin/                 Dashboard: lead'ler, çeviri kapsaması, içerik kuyruğu, persona/ML durumu
  /admin/translations/    Çeviri merkezi: model × dil matrisi, tek tıkla eksikleri çevir
  Menü iş akışına göre gruplanmıştır (Klinikler, İçerik, SEO, Lead'ler, Kişiselleştirme, Sistem).
"""
from datetime import timedelta

from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone

# (grup başlığı, ikon, [(app_label, model_name), ...]) — listede olmayanlar "Sistem" grubuna düşer
MENU = [
    ("Klinikler & Hekimler", "🏥", [("clinics", "clinic"), ("clinics", "doctor"), ("clinics", "clinicimage"),
                                   ("clinics", "beforeaftercase"), ("clinics", "review"), ("clinics", "city")]),
    ("Tedaviler & Fiyatlar", "🦷", [("treatments", "treatment"), ("treatments", "marketprice")]),
    ("Blog", "✍️", [("blog", "blogpost"), ("blog", "blogcategory"), ("blog", "relatedpost")]),
    ("SEO", "📈", [("seo", "keyword"), ("seo", "landingpage"), ("seo", "seotopic"), ("seo", "redirect")]),
    ("Lead'ler & Dönüşüm", "📥", [("tracking", "contactclick"), ("tracking", "lead"), ("tracking", "whatsappmatch"), ("tracking", "visitorsession"),
                                  ("tracking", "pageview"), ("tracking", "adconversion")]),
    ("Kişiselleştirme (Persona ML)", "🧠", [("persona", "personaarmstat"), ("persona", "personaexposure"),
                                           ("persona", "visitorsession"), ("persona", "mlmodelversion")]),
    ("Site & sayfa metinleri", "⚙️", [("core", "sitesettings"), ("core", "contentblock")]),
]


class DentalAdminSite(admin.AdminSite):
    site_header = "dentaltourism.tr"
    site_title = "dentaltourism.tr yönetim"
    index_title = "Kontrol paneli"
    index_template = "admin/dashboard.html"

    def get_urls(self):
        return [
            path("translations/", self.admin_view(self.translations_view), name="translation_center"),
        ] + super().get_urls()

    # ── Gruplu menü ───────────────────────────────────────────────────────
    def get_app_list(self, request, app_label=None):
        original = super().get_app_list(request, app_label)
        if app_label:
            return original
        models = {}
        for app in original:
            for m in app["models"]:
                models[(app["app_label"], m["object_name"].lower())] = m
        grouped, used = [], set()
        for title, icon, keys in MENU:
            items = [models[k] for k in keys if k in models]
            used.update(k for k in keys if k in models)
            if items:
                grouped.append({"name": f"{icon} {title}", "app_label": keys[0][0], "app_url": "",
                                "has_module_perms": True, "models": items})
        rest = [m for k, m in models.items() if k not in used]
        if rest:
            grouped.append({"name": "🔧 Sistem", "app_label": "auth", "app_url": "", "has_module_perms": True,
                            "models": sorted(rest, key=lambda m: m["name"])})
        return grouped

    # ── Dashboard ─────────────────────────────────────────────────────────
    def index(self, request, extra_context=None):
        extra_context = {**(extra_context or {}), **self._dashboard(request)}
        return super().index(request, extra_context)

    def _dashboard(self, request):
        from apps.blog.models import BlogPost
        from apps.clinics.models import Clinic
        from apps.localization.llm import is_configured
        from apps.persona.models import MLModelVersion, PersonaExposure
        from apps.seo.models import Keyword, LandingPage
        from django.db.models import Q

        from apps.tracking.models import Lead, PageView, VisitorSession

        now = timezone.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        leads = Lead.objects.all()
        if not request.user.is_superuser:
            leads = leads.filter(clinic__owner=request.user)
        since = now - timedelta(days=30)
        # Gerçek ziyaretçi = JS beacon'ı göndermiş oturum (page_views > 0); JS çalıştırmayan tarayıcılar/botlar sayılmaz
        humans = VisitorSession.objects.filter(created_at__gte=since, page_views__gt=0)
        humans_n = humans.count()
        contacted = humans.filter(Q(whatsapp_clicks__gte=1) | Q(phone_clicks__gte=1) | Q(is_lead=True)).count()
        junk_n = VisitorSession.objects.filter(created_at__gte=since, page_views=0).count()
        exposures = PersonaExposure.objects.filter(created_at__gte=since)
        exp_n = exposures.count()
        exp_c = exposures.filter(converted=True).count()
        return {
            "api_ready": is_configured(),
            "background": "thread pool",
            "kpi": {
                "leads_today": leads.filter(created_at__gte=today).count(),
                "leads_week": leads.filter(created_at__gte=today - timedelta(days=7)).count(),
                "leads_new": leads.filter(status="new").count(),
                "posts_review": BlogPost.objects.filter(status="review").count(),
                "posts_live": BlogPost.objects.filter(status="published").count(),
                "clinics_pending": Clinic.objects.filter(status="pending").count(),
                "keywords": Keyword.objects.count(),
                "keywords_open": Keyword.objects.filter(target_url="").exclude(status="ignored").count(),
                "landing_live": LandingPage.objects.filter(is_active=True, noindex=False).count(),
                "landing_total": LandingPage.objects.count(),
                "cr_30d": round(exp_c / exp_n * 100, 2) if exp_n else 0,
                "exposures_30d": exp_n,
                "visitors_30d": humans_n,
                "pageviews_30d": PageView.objects.filter(timestamp__gte=since).count(),
                "contact_rate_30d": round(contacted / humans_n * 100, 1) if humans_n else 0,
                "contacted_30d": contacted,
                "junk_30d": junk_n,
            },
            "latest_leads": leads.select_related("clinic", "treatment")[:8],
            "review_posts": BlogPost.objects.filter(status="review").order_by("-created_at")[:6],
            "coverage": self._coverage_summary(),
            "ml_model": MLModelVersion.objects.filter(is_active=True).first(),
        }

    def _coverage_summary(self):
        from apps.localization.models import LIVE_STATUSES, TranslationStatus
        from apps.localization.registry import all_specs

        langs = len(settings.LANGUAGES)
        rows = []
        for label, spec in all_specs().items():
            objs = spec.model.objects.count()
            if not objs:
                continue
            tr = spec.translation_model.objects
            live = tr.filter(status__in=LIVE_STATUSES).count() + objs  # + kaynak diller
            rows.append({
                "label": spec.model._meta.verbose_name_plural.title(),
                "url": f"/admin/{spec.model._meta.app_label}/{spec.model._meta.model_name}/",
                "objects": objs, "pct": round(live / (objs * langs) * 100),
                "failed": tr.filter(status=TranslationStatus.FAILED).count(),
                "outdated": tr.filter(status=TranslationStatus.OUTDATED).count(),
            })
        return rows

    # ── Çeviri merkezi ────────────────────────────────────────────────────
    def translations_view(self, request):
        from apps.localization.llm import is_configured
        from apps.localization.models import LIVE_STATUSES
        from apps.localization.registry import all_specs
        from apps.localization.service import sync_object

        specs = all_specs()
        if request.method == "POST":
            if not is_configured():
                messages.error(request, "ANTHROPIC_API_KEY .env içinde tanımlı değil.")
                return redirect("admin:translation_center")
            label = request.POST.get("model")
            jobs = 0
            for lbl, spec in specs.items():
                if label and lbl != label:
                    continue
                for obj in spec.model.objects.all():
                    if spec.should_auto_translate(obj):
                        jobs += len(sync_object(obj))
            messages.success(request, f"{jobs} çeviri işi arka planda başlatıldı. Sayfayı birkaç dakika sonra yenileyin.")
            return redirect("admin:translation_center")

        langs = [c for c, _ in settings.LANGUAGES]
        table = []
        for label, spec in specs.items():
            objs = list(spec.model.objects.all())
            if not objs:
                continue
            counts = {c: 0 for c in langs}
            for obj in objs:
                live = set(obj.translations.filter(status__in=LIVE_STATUSES).values_list("language_code", flat=True))
                live.add(obj.source_language)
                for c in live:
                    if c in counts:
                        counts[c] += 1
            table.append({"label": label, "name": spec.model._meta.verbose_name_plural.title(),
                          "total": len(objs),
                          "cells": [{"lang": c, "n": counts[c], "full": counts[c] == len(objs)} for c in langs]})
        context = {**self.each_context(request), "title": "Çeviri merkezi", "langs": langs, "table": table,
                   "api_ready": is_configured()}
        return TemplateResponse(request, "admin/translation_center.html", context)
