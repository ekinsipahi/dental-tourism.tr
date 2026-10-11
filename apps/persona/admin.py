from django.contrib import admin

from .models import MLModelVersion, PersonaArmStat, PersonaExposure, VisitorSession


@admin.register(VisitorSession)
class VisitorSessionAdmin(admin.ModelAdmin):
    list_display = ["session_key", "language_code", "device_type", "referral_source", "search_query",
                    "assigned_persona", "persona_confidence", "shown_persona", "converted", "total_sessions",
                    "last_seen"]
    list_filter = ["shown_persona", "assigned_persona", "converted", "device_type", "language_code",
                   "referral_source"]
    search_fields = ["session_key", "search_query"]
    readonly_fields = [f.name for f in VisitorSession._meta.fields]


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
