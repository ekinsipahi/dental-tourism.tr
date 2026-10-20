"""
apps/tracking/admin.py

Admin panelinden:
- Kim nerden geldi
- Kaç kez sayfaya baktı
- WhatsApp'a bastı mı
- Lead mi, converted mı
- Hangi kampanyadan
"""
from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.urls import reverse
from .models import AdConversion, ContactClick, Lead, PageView, SocialClick, VisitorSession, WhatsAppMatch


class MindFilter(admin.SimpleListFilter):
    """Aklındaki: fiyat / lüks / kalite / korku / şüphe … (persona motorunun tıklama anındaki teşhisi)."""
    title = "aklındaki"
    parameter_name = "mind"

    def lookups(self, request, model_admin):
        from apps.persona.mindset import LABELS

        return list(LABELS.items())

    def queryset(self, request, queryset):
        return queryset.filter(mind=self.value()) if self.value() else queryset


def mind_html(mind):
    """🧠 Ana teşhis + olasılık çubukları + neden (son kanıtlar)."""
    from apps.persona.mindset import LABELS

    if not mind:
        return "—"
    bars = format_html_join("", "<div style='white-space:nowrap'>{} <b>%{}</b></div>",
                            ((LABELS.get(p, p), round(v * 100)) for p, v in (mind.get("scores") or {}).items()))
    why = format_html_join("", "<li>{} {}</li>",
                           ((LABELS.get(w.get("p"), "").split(" ")[0], (w.get("l") or "")[:60])
                            for w in (mind.get("why") or [])[:5]))
    level = {"weak": ("zayıf sinyal", "#9e9e9e"), "medium": ("orta", "#f59e0b"), "strong": ("güçlü", "#16a34a")}.get(
        mind.get("level", ""), ("", "#9e9e9e"))
    title = mind.get("label", "") if mind.get("level") != "weak" else f"{LABELS['unknown']} ({mind.get('label', '')}?)"
    return format_html("<strong>{}</strong> <span style='color:{};font-size:11px'>● {} · {} sinyal</span>{}"
                       "<details><summary style='color:#888;cursor:pointer'>neden?</summary>"
                       "<ul style='margin:0;padding-left:1rem;color:#555;font-size:11px'>{}</ul></details>",
                       title, level[1], level[0], mind.get("signals", 0), bars, why)


@admin.register(VisitorSession)
class VisitorSessionAdmin(admin.ModelAdmin):
    list_display = [
        "session_short", "traffic_source_badge", "country_flag",
        "device_icon", "intent_score_bar", "conversion_flags",
        "page_views", "total_time_display", "last_seen",
    ]
    list_filter  = [
        "traffic_source", "device_type", "ip_country",
        "is_lead", "is_converted", "is_qualified",
        "whatsapp_matched",
    ]
    search_fields = ["session_key", "gclid", "fbclid", "ip_city", "utm_campaign"]
    readonly_fields = [f.name for f in VisitorSession._meta.fields] + ["conversion_intent_score", "has_paid_source"]
    list_per_page = 50
    date_hierarchy = "created_at"

    fieldsets = [
        ("Session", {"fields": ["session_key", "created_at", "last_seen", "session_count"]}),
        ("Traffic Source", {"fields": [
            "traffic_source", "landing_page", "referrer_url",
            "gclid", "google_campaign", "google_adgroup", "google_keyword",
            "fbclid", "fb_campaign", "fb_adset", "fb_ad",
            "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
        ]}),
        ("Device & Location", {"fields": [
            "visitor_id", "ip_address", "ip_hash", "ip_country", "ip_city", "ip_region", "ip_postal", "ip_org",
            "ip_timezone", "ip_loc", "geo_source",
            "device_type", "device_brand", "device_model",
            "os_name", "os_version", "browser_name", "browser_version",
            "screen_width", "screen_height", "language_code",
        ]}),
        ("Behavior", {"fields": [
            "page_views", "total_time_sec", "avg_scroll_depth",
            "whatsapp_clicks", "phone_clicks", "form_starts", "form_submits",
            "cta_clicks", "video_plays", "map_clicks",
        ]}),
        ("WhatsApp Match", {"fields": [
            "whatsapp_clicked_at", "whatsapp_matched",
            "whatsapp_match_phone", "whatsapp_match_time",
        ]}),
        ("Conversion", {"fields": [
            "is_lead", "is_converted", "is_qualified",
            "lead_at", "converted_at", "assigned_persona",
            "conversion_intent_score",
        ]}),
        ("Notes", {"fields": ["notes"]}),
    ]

    def session_short(self, obj):
        return format_html('<code style="font-size:.75rem">{}</code>', obj.session_key[:16] + "...")
    session_short.short_description = "Session"

    def traffic_source_badge(self, obj):
        colors = {
            "google_ads":    ("#1a73e8", "GA"),
            "meta_ads":      ("#1877f2", "META"),
            "google_organic": ("#34a853", "ORG"),
            "bing_organic":  ("#00809d", "BING"),
            "social":        ("#e91e63", "SOC"),
            "referral":      ("#ff9800", "REF"),
            "direct":        ("#757575", "DIR"),
            "email":         ("#9c27b0", "EMAIL"),
            "whatsapp_direct": ("#25d366", "WA"),
            "unknown":       ("#9e9e9e", "?"),
        }
        color, label = colors.get(obj.traffic_source, ("#9e9e9e", "?"))
        gclid_badge = ' <span style="background:#ffd600;color:#000;padding:1px 4px;border-radius:3px;font-size:.6rem;">GCLID</span>' if obj.gclid else ""
        fbclid_badge = ' <span style="background:#1877f2;color:#fff;padding:1px 4px;border-radius:3px;font-size:.6rem;">FB</span>' if obj.fbclid else ""
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:.72rem;font-weight:700">{}</span>{}{}',
            color, label, format_html(gclid_badge), format_html(fbclid_badge)
        )
    traffic_source_badge.short_description = "Source"

    def country_flag(self, obj):
        flags = {
            "TR": "🇹🇷", "DE": "🇩🇪", "NL": "🇳🇱", "GB": "🇬🇧",
            "FR": "🇫🇷", "BE": "🇧🇪", "AT": "🇦🇹", "CH": "🇨🇭",
            "RU": "🇷🇺", "UA": "🇺🇦", "US": "🇺🇸", "SE": "🇸🇪",
            "NO": "🇳🇴", "DK": "🇩🇰", "FI": "🇫🇮", "PL": "🇵🇱",
        }
        flag = flags.get(obj.ip_country, "🌍")
        city = f" {obj.ip_city}" if obj.ip_city else ""
        return format_html("{} {}{}", flag, obj.ip_country or "–", city)
    country_flag.short_description = "Location"

    def device_icon(self, obj):
        icons = {"mobile": "📱", "tablet": "📊", "desktop": "💻"}
        icon = icons.get(obj.device_type, "❓")
        brand = f" {obj.device_brand}" if obj.device_brand else ""
        os = f" {obj.os_name}" if obj.os_name else ""
        return format_html("{}{}{}", icon, brand, os)
    device_icon.short_description = "Device"

    def intent_score_bar(self, obj):
        score = obj.conversion_intent_score
        color = "#16a34a" if score >= 60 else "#d97706" if score >= 30 else "#dc2626"
        return format_html(
            '<div style="display:flex;align-items:center;gap:6px;">'
            '<div style="width:60px;height:8px;background:#e5e7eb;border-radius:4px;overflow:hidden">'
            '<div style="width:{}%;height:100%;background:{};border-radius:4px"></div></div>'
            '<span style="font-size:.75rem;color:{};font-weight:700">{}</span>'
            '</div>',
            score, color, color, score
        )
    intent_score_bar.short_description = "Intent"

    def conversion_flags(self, obj):
        flags = []
        if obj.whatsapp_clicks > 0:
            flags.append(f'<span style="color:#25d366">💬×{obj.whatsapp_clicks}</span>')
        if obj.phone_clicks > 0:
            flags.append(f'<span style="color:#2563eb">📞×{obj.phone_clicks}</span>')
        if obj.form_submits > 0:
            flags.append(f'<span style="color:#7c3aed">📝×{obj.form_submits}</span>')
        if obj.is_lead:
            flags.append('<span style="background:#fef3c7;color:#92400e;padding:1px 5px;border-radius:3px;font-size:.65rem">LEAD</span>')
        if obj.is_qualified:
            flags.append('<span style="background:#d1fae5;color:#065f46;padding:1px 5px;border-radius:3px;font-size:.65rem">QUAL</span>')
        if obj.is_converted:
            flags.append('<span style="background:#dbeafe;color:#1e40af;padding:1px 5px;border-radius:3px;font-size:.65rem">CONV</span>')
        if obj.whatsapp_matched:
            flags.append('<span style="background:#dcfce7;color:#166534;padding:1px 5px;border-radius:3px;font-size:.65rem">WA✓</span>')
        return format_html(" ".join(flags)) if flags else format_html('<span style="color:#9ca3af">–</span>')
    conversion_flags.short_description = "Actions"

    def total_time_display(self, obj):
        t = obj.total_time_sec
        if t < 60:
            return f"{t}s"
        return f"{t//60}m {t%60}s"
    total_time_display.short_description = "Time"



def _location_html(s):
    """IP konumu; IP tarayıcı saat dilimiyle çelişiyorsa (proxy / VPN) saat dilimindeki ülke + uyarı."""
    if s.via_proxy:
        return format_html("{} <strong>{}</strong> {}<br><span style='color:#b45309'>🛡 proxy/VPN — IP: {} {}</span>",
                           _flag(s.real_country), s.real_country, s.timezone_name, s.ip_country, (s.ip_org or "")[:30])
    place = ", ".join(filter(None, [s.ip_city, s.ip_region])) or "—"
    return format_html("{} <strong>{}</strong> {}<br><span style='color:#888'>{}</span>", _flag(s.ip_country),
                       s.ip_country or "?", place, (s.ip_org or "")[:40])

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    @admin.display(description="🧠 Aklındaki", ordering="mind")
    def lead_mind(self, o):
        return mind_html(o.mindset)

    @admin.display(description="Konum (ipinfo)")
    def lead_location(self, o):
        s = o.session
        if s:
            return _location_html(s)
        return format_html("{} <strong>{}</strong> {}", _flag(o.ip_country), o.ip_country or "?", o.ip_city or "—")

    @admin.display(description="Cihaz / geçmiş")
    def lead_device(self, o):
        s = o.session
        if not s:
            return o.device_type or "—"
        icon = {"mobile": "📱", "tablet": "📲", "desktop": "💻"}.get(s.device_type, "❔")
        model = " ".join(filter(None, [s.device_brand, s.device_model])) or s.device_type
        return format_html("{} {} · {} {}<br><span style='color:#888'>{}. ziyaret · 📞{} 💬{}</span>", icon, model,
                           s.os_name, s.browser_name, s.session_count, s.phone_clicks, s.whatsapp_clicks)

    list_display = [
        "name_or_anon", "clinic", "persona", "source_badge", "status_badge",
        "contact_info", "lead_mind", "traffic_info", "lead_location", "lead_device",
        "wa_match_status", "created_at",
    ]
    list_filter  = ["status", MindFilter, "clinic", "source", "traffic_source", "persona", "ip_country", "language", "whatsapp_matched"]
    search_fields = ["name", "phone", "email", "gclid", "fbclid", "utm_campaign"]

    date_hierarchy = "created_at"
    list_per_page = 30

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("clinic", "treatment")
        return qs if request.user.is_superuser else qs.filter(clinic__owner=request.user)

    fieldsets = [
        ("Contact", {"fields": ["name", "phone", "email", "message"]}),
        ("Status", {"fields": ["clinic", "treatment", "source", "status", "persona", "notes", "assigned_to"]}),
        ("Traffic", {"fields": [
            "traffic_source", "gclid", "fbclid",
            "utm_campaign", "utm_source", "page", "language",
        ]}),
        ("Device & Location", {"fields": ["device_type", "ip_country", "ip_city"]}),
        ("Conversion", {"fields": [
            "conversion_value", "currency",
            "contacted_at", "qualified_at", "booked_at", "treated_at",
        ]}),
        ("WhatsApp", {"fields": ["whatsapp_matched", "whatsapp_match_confidence"]}),
    ]

    def name_or_anon(self, obj):
        return obj.name or format_html('<span style="color:#9ca3af">Anonymous</span>')
    name_or_anon.short_description = "Name"

    def source_badge(self, obj):
        colors = {
            "form": "#7c3aed", "whatsapp": "#25d366",
            "phone": "#2563eb", "chatbot": "#f59e0b",
        }
        color = colors.get(obj.source, "#9ca3af")
        labels = {"form": "📝 Form", "whatsapp": "💬 WA", "phone": "📞 Phone", "chatbot": "🤖 Bot"}
        label = labels.get(obj.source, obj.source)
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:.72rem">{}</span>',
            color, label
        )
    source_badge.short_description = "Source"

    def status_badge(self, obj):
        colors = {
            "new": "#6b7280", "contacted": "#2563eb", "qualified": "#d97706",
            "booked": "#7c3aed", "treated": "#16a34a", "lost": "#dc2626",
        }
        color = colors.get(obj.status, "#9ca3af")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:.72rem">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def contact_info(self, obj):
        parts = []
        if obj.phone:
            parts.append(format_html('<a href="tel:{}" style="color:#2563eb">{}</a>', obj.phone, obj.phone))
        if obj.email:
            parts.append(format_html('<span style="color:#6b7280">{}</span>', obj.email))
        return format_html(" | ".join([p for p in parts])) if parts else format_html("–")
    contact_info.short_description = "Contact"

    def traffic_info(self, obj):
        src = obj.traffic_source or "–"
        extra = ""
        if obj.gclid:
            extra = format_html(' <span style="background:#ffd600;color:#000;padding:1px 4px;border-radius:3px;font-size:.6rem">GCLID</span>')
        elif obj.fbclid:
            extra = format_html(' <span style="background:#1877f2;color:#fff;padding:1px 4px;border-radius:3px;font-size:.6rem">FB</span>')
        if obj.utm_campaign:
            extra += format_html(' <span style="color:#6b7280;font-size:.7rem">{}</span>', obj.utm_campaign[:20])
        return format_html("{}{}", src, extra)
    traffic_info.short_description = "Traffic"

    def device_country(self, obj):
        flags = {"TR":"🇹🇷","DE":"🇩🇪","NL":"🇳🇱","GB":"🇬🇧","FR":"🇫🇷","RU":"🇷🇺","BE":"🇧🇪"}
        icons = {"mobile":"📱","tablet":"📊","desktop":"💻"}
        flag = flags.get(obj.ip_country, "🌍")
        icon = icons.get(obj.device_type, "❓")
        return format_html("{} {} {}", flag, obj.ip_country or "–", icon)
    device_country.short_description = "Loc/Dev"

    def wa_match_status(self, obj):
        if not obj.whatsapp_matched:
            return format_html('<span style="color:#9ca3af">–</span>')
        conf = obj.whatsapp_match_confidence
        color = "#16a34a" if conf >= 0.8 else "#d97706"
        return format_html(
            '<span style="color:{}">✓ WA {:.0%}</span>', color, conf
        )
    wa_match_status.short_description = "WA Match"


@admin.register(WhatsAppMatch)
class WhatsAppMatchAdmin(admin.ModelAdmin):
    list_display = ["wa_phone", "match_confidence_bar", "time_diff_display",
                    "is_manual", "session_link", "matched_at"]
    list_filter  = ["is_manual"]
    readonly_fields = [f.name for f in WhatsAppMatch._meta.fields]

    def match_confidence_bar(self, obj):
        score = int(obj.match_confidence * 100)
        color = "#16a34a" if score >= 80 else "#d97706" if score >= 50 else "#dc2626"
        return format_html(
            '<span style="color:{};font-weight:700">{:.0%}</span>',
            color, obj.match_confidence
        )
    match_confidence_bar.short_description = "Confidence"

    def time_diff_display(self, obj):
        if obj.time_diff_seconds is None:
            return "–"
        t = obj.time_diff_seconds
        return f"{t//60}m {t%60}s" if t >= 60 else f"{t}s"
    time_diff_display.short_description = "Time Diff"

    def session_link(self, obj):
        if not obj.session:
            return "–"
        url = reverse("admin:tracking_visitorsession_change", args=[obj.session.id])
        return format_html('<a href="{}">{}</a>', url, obj.session.session_key[:12] + "...")
    session_link.short_description = "Session"

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ["url", "title", "timestamp", "session"]
    search_fields = ["url", "title"]
    readonly_fields = [f.name for f in PageView._meta.fields]


@admin.register(AdConversion)
class AdConversionAdmin(admin.ModelAdmin):
    list_display = ["platform", "conversion_name", "conversion_value", "currency", "status", "created_at"]
    list_filter = ["platform", "status"]



# ═════════════════════════════════════════════════════════════════════════════
# 📞 İletişim tıklamaları — telefon / WhatsApp / form: kim, ne zaman, hangi cihaz, nereden
# ═════════════════════════════════════════════════════════════════════════════
def _flag(cc):
    cc = (cc or "").upper()
    if len(cc) != 2:
        return ""
    return "".join(chr(0x1F1E6 + ord(c) - 65) for c in cc)


_TYPE = {"phone_click": ("☎️ Telefon denemesi (hat yanıtlanmıyor)", "#64748b"), "whatsapp_click": ("💬 WhatsApp", "#16a34a"),
         "form_submit": ("📝 Form", "#9333ea"), "instagram_click": ("📸 Instagram", "#d6249f"),
         "youtube_click": ("▶️ YouTube", "#dc2626"), "maps_click": ("📍 Yol tarifi / Google", "#2563eb"),
         "email_click": ("✉️ E-posta", "#0f766e")}
_SRC = {"google_ads": ("Google Ads", "#1a73e8"), "meta_ads": ("Meta Ads", "#1877f2"),
        "google_organic": ("Google organik", "#34a853"), "bing_organic": ("Bing", "#00809d"), "social": ("Sosyal", "#e91e63"),
        "referral": ("Referans", "#ff9800"), "direct": ("Direkt", "#757575"), "email": ("E-posta", "#9c27b0")}


@admin.register(ContactClick)
class ContactClickAdmin(admin.ModelAdmin):
    list_display = ["when", "action", "mind_col", "button", "visitor", "location", "device", "source", "page",
                    "persona_stage"]
    list_filter = ["event_type", MindFilter, "session__ip_country", "session__device_type", "session__traffic_source",
                   "persona", "stage", "language", "position"]
    search_fields = ["session__visitor_id", "session__session_key", "session__ip_city", "session__ip_region",
                     "session__ip_org", "session__google_keyword", "session__utm_term", "session__utm_campaign",
                     "session__gclid", "page_url", "label"]
    date_hierarchy = "timestamp"
    list_per_page = 100
    actions = ["export_csv"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Zaman", ordering="timestamp")
    def when(self, o):
        from django.utils import timezone

        t = timezone.localtime(o.timestamp)
        return format_html("<strong>{}</strong><br><span style='color:#888'>{}</span>", t.strftime("%H:%M:%S"),
                           t.strftime("%d.%m.%Y"))

    @admin.display(description="Eylem", ordering="event_type")
    def action(self, o):
        label, color = _TYPE.get(o.event_type, (o.event_type, "#666"))
        if o.event_type == "whatsapp_click" and (o.data or {}).get("element") == "whatsapp_call":
            label, color = "📞 WhatsApp arama", "#15803d"
        return format_html('<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;'
                           'white-space:nowrap">{}</span>', color, label)

    @admin.display(description="🧠 Aklındaki", ordering="mind")
    def mind_col(self, o):
        return mind_html(o.mindset)

    @admin.display(description="Buton / yer")
    def button(self, o):
        return format_html("{}<br><span style='color:#888'>{}</span>", (o.label or "—")[:40], o.position or "")

    @admin.display(description="Ziyaretçi")
    def visitor(self, o):
        s = o.session
        url = reverse("admin:tracking_visitorsession_change", args=[s.pk])
        vid = (s.visitor_id or s.session_key or "")[:10]
        return format_html('<a href="{}"><code>{}</code></a><br><span style="color:#888">{}. ziyaret · 📞{} 💬{} 📝{}</span>',
                           url, vid, s.session_count, s.phone_clicks, s.whatsapp_clicks, s.form_submits)

    @admin.display(description="Konum (ipinfo)", ordering="session__ip_country")
    def location(self, o):
        return _location_html(o.session)

    @admin.display(description="Cihaz", ordering="session__device_type")
    def device(self, o):
        s = o.session
        icon = {"mobile": "📱", "tablet": "📲", "desktop": "💻"}.get(s.device_type, "❔")
        model = " ".join(filter(None, [s.device_brand, s.device_model])) or s.device_type or "—"
        sw = f"{s.os_name} {s.os_version}".strip()
        br = f"{s.browser_name} {s.browser_version}".strip()
        return format_html("{} {}<br><span style='color:#888'>{} · {}</span>", icon, model, sw or "—", br or "—")

    @admin.display(description="Kaynak", ordering="session__traffic_source")
    def source(self, o):
        s = o.session
        label, color = _SRC.get(s.traffic_source, (s.traffic_source or "?", "#666"))
        detail = s.google_keyword or s.utm_term or s.google_campaign or s.utm_campaign or (
            "gclid" if s.gclid else "") or (s.referrer_url or "")[:40]
        return format_html('<span style="color:{};font-weight:600">{}</span><br><span style="color:#888">{}</span>',
                           color, label, detail[:50])

    @admin.display(description="Sayfa")
    def page(self, o):
        return format_html('<a href="{}" target="_blank">{}</a>', o.page_url, (o.page_url or "—")[:45])

    @admin.display(description="Persona / aşama", ordering="persona")
    def persona_stage(self, o):
        return format_html("{}<br><span style='color:#888'>{} · {}</span>", o.persona or "—", o.stage or "",
                           (o.language or "").upper())

    @admin.action(description="⬇️ CSV olarak indir")
    def export_csv(self, request, queryset):
        import csv

        from django.http import HttpResponse
        from django.utils import timezone

        from apps.persona.mindset import describe

        resp = HttpResponse(content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="iletisim-tiklamalari.csv"'
        resp.write("\ufeff")
        w = csv.writer(resp)
        w.writerow(["zaman", "eylem", "buton", "yer", "ziyaretci_id", "ziyaret_no", "ip", "ulke", "sehir", "bolge",
                    "saglayici", "cihaz", "marka", "model", "isletim_sistemi", "tarayici", "kaynak", "anahtar_kelime",
                    "kampanya", "gclid", "sayfa", "persona", "asama", "dil", "aklindaki", "aklindaki_detay"])
        for o in queryset.select_related("session"):
            s = o.session
            w.writerow([timezone.localtime(o.timestamp).strftime("%Y-%m-%d %H:%M:%S"), o.event_type, o.label, o.position,
                        s.visitor_id, s.session_count, s.ip_address or "", s.ip_country, s.ip_city, s.ip_region, s.ip_org,
                        s.device_type, s.device_brand, s.device_model, f"{s.os_name} {s.os_version}".strip(),
                        f"{s.browser_name} {s.browser_version}".strip(), s.traffic_source,
                        s.google_keyword or s.utm_term, s.google_campaign or s.utm_campaign, s.gclid or "",
                        o.page_url, o.persona, o.stage, o.language, o.mind, describe(o.mindset)])
        return resp


@admin.register(SocialClick)
class SocialClickAdmin(ContactClickAdmin):
    """Instagram / YouTube / yol tarifi / e-posta — iletişim listesinden ayrı (iletişim sayılmaz)."""
    list_filter = ["event_type", "session__ip_country", "session__device_type", "session__traffic_source", "position"]

