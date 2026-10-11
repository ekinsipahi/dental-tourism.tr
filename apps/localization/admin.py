from django.conf import settings
from django.contrib import admin, messages
from django.utils.html import format_html, format_html_join

from .models import LIVE_STATUSES, TranslationStatus

STATUS_COLORS = {
    TranslationStatus.MACHINE: "#16a34a",
    TranslationStatus.REVIEWED: "#2563eb",
    TranslationStatus.OUTDATED: "#d97706",
    TranslationStatus.FAILED: "#dc2626",
    TranslationStatus.PENDING: "#9ca3af",
}


class TranslationInlineBase(admin.StackedInline):
    """Çeviri satırları — insan düzeltmesi yapılınca status'u 'reviewed' yapın."""
    extra = 0
    classes = ["collapse"]
    readonly_fields = ["translated_at", "model_used", "error"]


class TranslatableAdmin(admin.ModelAdmin):
    actions = ["action_translate_missing", "action_retranslate_all"]

    @admin.display(description="Diller")
    def translation_badge(self, obj):
        cov = obj.translation_coverage()
        pct = int(cov["done"] / cov["total"] * 100) if cov["total"] else 0
        color = "#16a34a" if pct >= 90 else "#d97706" if pct >= 40 else "#dc2626"
        return format_html('<b style="color:{}">{}/{}</b>', color, cov["done"], cov["total"])

    @admin.display(description="Çeviri durumu")
    def translation_matrix(self, obj):
        if not obj or not obj.pk:
            return "—"
        statuses = obj.translation_coverage()["statuses"]
        chips = []
        for code, _ in settings.LANGUAGES:
            if code == obj.source_language:
                chips.append((code.upper(), "#111827", "kaynak"))
                continue
            st = statuses.get(code)
            chips.append((code.upper(), STATUS_COLORS.get(st, "#e5e7eb"), st or "yok"))
        return format_html(
            '<div style="display:flex;flex-wrap:wrap;gap:4px">{}</div>',
            format_html_join("", '<span title="{2}" style="background:{1};color:#fff;padding:2px 7px;'
                                 'border-radius:4px;font-size:11px;font-weight:700">{0}</span>', chips),
        )

    @admin.action(description="🌍 Eksik / eskimiş dilleri AI ile çevir")
    def action_translate_missing(self, request, queryset):
        from .llm import is_configured
        from .service import sync_object

        if not is_configured():
            self.message_user(request, "ANTHROPIC_API_KEY tanımlı değil (.env).", messages.ERROR)
            return
        total = sum(len(sync_object(obj)) for obj in queryset)
        self.message_user(request, f"{total} çeviri işi arka planda başlatıldı.", messages.SUCCESS)

    @admin.action(description="♻️ Tüm dilleri yeniden çevir (insan onaylılar hariç)")
    def action_retranslate_all(self, request, queryset):
        from .llm import is_configured
        from .service import sync_object

        if not is_configured():
            self.message_user(request, "ANTHROPIC_API_KEY tanımlı değil (.env).", messages.ERROR)
            return
        for obj in queryset:
            obj.translations.exclude(status=TranslationStatus.REVIEWED).update(source_hash="")
            sync_object(obj)
        self.message_user(request, "Yeniden çeviri başlatıldı.", messages.SUCCESS)


__all__ = ["TranslatableAdmin", "TranslationInlineBase", "LIVE_STATUSES"]
