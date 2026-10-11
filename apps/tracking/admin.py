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
from django.utils.html import format_html
from django.urls import reverse
from .models import VisitorSession, PageView, Lead, WhatsAppMatch, AdConversion


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
            "ip_hash", "ip_country", "ip_city",
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


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        "name_or_anon", "clinic", "persona", "source_badge", "status_badge",
        "contact_info", "traffic_info", "device_country",
        "wa_match_status", "created_at",
    ]
    list_filter  = ["status", "clinic", "source", "traffic_source", "persona", "ip_country", "language", "whatsapp_matched"]
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
