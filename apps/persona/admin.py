from django.contrib import admin
from django.utils.html import format_html, format_html_join

from .models import MLModelVersion, PersonaArmStat, PersonaExposure, VisitorSession


@admin.register(VisitorSession)
class VisitorSessionAdmin(admin.ModelAdmin):
    list_display = ["session_key", "mind_now", "language_code", "device_type", "referral_source", "search_query",
                    "shown_persona", "converted", "total_sessions", "last_seen"]
    list_filter = ["shown_persona", "assigned_persona", "converted", "device_type", "language_code",
                   "referral_source"]
    search_fields = ["session_key", "visitor_id", "search_query"]
    readonly_fields = ["mind_now", "evidence_log"] + [f.name for f in VisitorSession._meta.fields]

    @admin.display(description="🧠 Şu an aklındaki")
    def mind_now(self, o):
        from apps.tracking.admin import mind_html

        from .mindset import snapshot

        return mind_html(snapshot(o))

    @admin.display(description="Kanıt günlüğü (sayaç)")
    def evidence_log(self, o):
        from .mindset import LABELS

        rows = reversed(o.evidence or [])
        return format_html("<table style='font-size:12px'>{}</table>", format_html_join(
            "", "<tr><td style='color:#888'>{}</td><td>{}</td><td>{}</td><td>{}</td><td>+{}</td></tr>",
            ((e.get("at", "")[5:16].replace("T", " "), e.get("k", ""), e.get("l", ""), LABELS.get(e.get("p"), ""),
              e.get("w", "")) for e in rows)))


@admin.register(PersonaExposure)
class PersonaExposureAdmin(admin.ModelAdmin):
    list_display = ["created_at", "segment", "persona", "inferred_persona", "policy", "propensity",
                    "converted", "conversion_type"]
    list_filter = ["persona", "policy", "converted", "conversion_type"]
    readonly_fields = [f.name for f in PersonaExposure._meta.fields]


@admin.register(PersonaArmStat)
class PersonaArmStatAdmin(admin.ModelAdmin):
    list_display = ["segment", "persona", "impressions", "conversions", "rate_pct"]
    list_filter = ["persona"]
    search_fields = ["segment"]

    @admin.display(description="CR %")
    def rate_pct(self, obj):
        return f"{obj.rate * 100:.2f}"


@admin.register(MLModelVersion)
class MLModelVersionAdmin(admin.ModelAdmin):
    list_display = ["version", "kind", "is_active", "accuracy", "training_samples", "positives", "trained_at"]
    list_editable = ["is_active"]
    readonly_fields = ["metrics", "feature_names"]
