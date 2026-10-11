"""
Klinik admin'i — çok klinikli yapı:
  - Superuser her şeyi görür.
  - "Clinic owners" grubundaki staff kullanıcılar sadece owner'ı oldukları klinikleri
    ve onlara bağlı hekim/fiyat/yorum/lead kayıtlarını görür, status'u değiştiremez.
"""
from django.contrib import admin

from django import forms
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import format_html

from apps.core.admin import image_preview
from apps.localization.admin import TranslatableAdmin, TranslationInlineBase

from .models import (BeforeAfterCase, City, CityTranslation, Clinic, ClinicImage, ClinicLink, ClinicTranslation,
                     ClinicTreatment, Doctor, DoctorTranslation, Review)


class OwnerScopedMixin:
    """Superuser olmayan staff kullanıcıları kendi kliniklerine sınırlar."""
    clinic_lookup = "clinic__owner"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(**{self.clinic_lookup: request.user})

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "clinic" and not request.user.is_superuser:
            kwargs["queryset"] = Clinic.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CityTranslationInline(TranslationInlineBase):
    model = CityTranslation


@admin.register(City)
class CityAdmin(TranslatableAdmin):
    list_display = ["name", "country_code", "is_active", "order", "translation_badge"]
    list_editable = ["is_active", "order"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["translation_matrix"]
    inlines = [CityTranslationInline]


class ClinicTranslationInline(TranslationInlineBase):
    model = ClinicTranslation


class ClinicTreatmentInline(admin.TabularInline):
    model = ClinicTreatment
    extra = 0
    fields = ["treatment", "price_from", "price_to", "currency", "price_unit", "stay_days", "visits",
              "warranty_years", "brands", "is_active"]


class ClinicLinkInline(admin.TabularInline):
    model = ClinicLink
    extra = 1
    fields = ["platform", "url", "label", "order"]
    verbose_name = "Profil / sosyal medya linki"
    verbose_name_plural = "Profil & sosyal medya linkleri (Google Business, Instagram, TikTok, Trustpilot…)"


class ClinicImageInline(admin.TabularInline):
    model = ClinicImage
    extra = 1
    fields = ["image_preview", "image", "image_url", "alt", "kind", "show_in_hero", "order"]
    readonly_fields = ["image_preview"]
    image_preview = image_preview("src", 70)


class BeforeAfterInline(admin.TabularInline):
    model = BeforeAfterCase
    extra = 0
    fields = ["before_preview", "before_image", "before_image_url", "after_preview", "after_image", "after_image_url",
              "treatment", "caption", "patient_consent", "is_published", "order"]
    readonly_fields = ["before_preview", "after_preview"]
    before_preview = image_preview("before_src", 60, "Önce")
    after_preview = image_preview("after_src", 60, "Sonra")


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiFileField(forms.FileField):
    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(d, initial) for d in data]
        return [single(data, initial)] if data else []


class BulkImageForm(forms.Form):
    clinic = forms.ModelChoiceField(queryset=Clinic.objects.all(), label="Klinik")
    kind = forms.ChoiceField(choices=ClinicImage.KIND_CHOICES, label="Tür")
    alt_prefix = forms.CharField(label="Alt metin (SEO)", max_length=150,
                                 help_text="Ör: 'Dental clinic Şişli Istanbul treatment room' — sonuna sıra no eklenir")
    show_in_hero = forms.BooleanField(required=False, initial=False, label="Slider'da göster")
    images = MultiFileField(widget=MultiFileInput(attrs={"accept": "image/*"}), label="Görseller (çoklu seçim)",
                            required=False)
    urls = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}), required=False,
                           label="…veya görsel linkleri (her satıra bir URL)")

    def clean(self):
        cd = super().clean()
        if not cd.get("images") and not (cd.get("urls") or "").strip():
            raise forms.ValidationError("Dosya seçin veya en az bir görsel linki girin.")
        return cd


@admin.register(ClinicImage)
class ClinicImageAdmin(admin.ModelAdmin):
    list_display = ["thumb", "alt", "clinic", "kind", "show_in_hero", "order"]
    list_editable = ["alt", "kind", "show_in_hero", "order"]
    list_filter = ["clinic", "kind", "show_in_hero"]
    readonly_fields = ["image_preview"]
    fields = ["clinic", "image", "image_url", "image_preview", "alt", "kind", "show_in_hero", "order"]
    image_preview = image_preview("src", 220)
    change_list_template = "admin/clinics/clinicimage/change_list.html"

    @admin.display(description="")
    def thumb(self, obj):
        return format_html('<img src="{}" class="dt-thumb">', obj.src) if obj.src else "—"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(clinic__owner=request.user)

    def get_urls(self):
        return [path("bulk-upload/", self.admin_site.admin_view(self.bulk_upload), name="clinics_clinicimage_bulk")] \
            + super().get_urls()

    def bulk_upload(self, request):
        form = BulkImageForm(request.POST or None, request.FILES or None)
        if not request.user.is_superuser:
            form.fields["clinic"].queryset = Clinic.objects.filter(owner=request.user)
        if request.method == "POST" and form.is_valid():
            cd = form.cleaned_data
            start = ClinicImage.objects.filter(clinic=cd["clinic"]).count()
            sources = [("file", f) for f in cd["images"]] + \
                [("url", u.strip()) for u in (cd.get("urls") or "").splitlines() if u.strip().startswith("http")]
            for i, (kind, src) in enumerate(sources, start=1):
                ClinicImage.objects.create(clinic=cd["clinic"], kind=cd["kind"],
                                           image=src if kind == "file" else None, image_url=src if kind == "url" else "",
                                           alt=f"{cd['alt_prefix']} {start + i}".strip(),
                                           show_in_hero=cd["show_in_hero"], order=start + i)
            messages.success(request, f"{len(sources)} görsel eklendi. Alt metinleri listeden düzenleyebilirsiniz.")
            return redirect("admin:clinics_clinicimage_changelist")
        return render(request, "admin/clinics/clinicimage/bulk_upload.html",
                      {**self.admin_site.each_context(request), "form": form, "title": "Toplu görsel yükle",
                       "opts": self.model._meta})


@admin.register(Clinic)
class ClinicAdmin(OwnerScopedMixin, TranslatableAdmin):
    clinic_lookup = "owner"
    list_display = ["name", "city", "status", "is_primary", "is_verified", "google_rating", "translation_badge"]
    list_filter = ["status", "city", "is_verified", "is_featured"]
    search_fields = ["name", "legal_name", "address"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["translation_matrix", "created_at", "updated_at", "logo_preview", "cover_preview"]
    logo_preview = image_preview("logo_src", 60)
    cover_preview = image_preview("cover_src", 140)
    inlines = [ClinicLinkInline, ClinicTreatmentInline, ClinicImageInline, BeforeAfterInline, ClinicTranslationInline]
    fieldsets = [
        ("Yönetim", {"fields": ["status", "owner", "is_primary", "is_featured", "is_verified", "order"]}),
        ("Kimlik", {"fields": ["name", "short_name", "slug", "legal_name", "license_number",
                               ("logo", "logo_url", "logo_preview"), ("cover_image", "cover_image_url", "cover_preview")]}),
        ("İçerik (kaynak dil)", {"fields": ["source_language", "auto_translate", "tagline", "short_description",
                                            "description", "faq", "meta_title", "meta_description", "translation_matrix"]}),
        ("Konum", {"fields": ["city", "district", "neighborhood", "address", "postal_code", "latitude",
                              "longitude", "maps_url", "maps_embed_url"]}),
        ("İletişim & profiller", {"fields": ["phone", "whatsapp", "email", "website", "google_business_url",
                                            "google_review_url", "instagram", "youtube_url", "facebook_url"],
                                 "description": "Diğer sosyal medya / profil linkleri için aşağıdaki 'Clinic links' bölümünü kullanın."}),
        ("Güven sinyalleri", {"fields": ["founded_year", "years_experience", "patients_treated", "countries_served",
                                         "google_rating", "google_review_count", "google_place_id",
                                         "languages_spoken", "accreditations", "opening_hours", "price_range",
                                         "offers_airport_transfer", "offers_hotel_booking"]}),
        ("Zaman", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            ro += ["status", "owner", "is_primary", "is_featured", "is_verified"]
        return ro


class DoctorTranslationInline(TranslationInlineBase):
    model = DoctorTranslation


@admin.register(Doctor)
class DoctorAdmin(OwnerScopedMixin, TranslatableAdmin):
    list_display = ["thumb", "full_name", "clinic", "is_lead_doctor", "is_active", "translation_badge"]
    list_display_links = ["thumb", "full_name"]
    list_filter = ["clinic", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["translation_matrix", "photo_preview"]
    photo_preview = image_preview("photo_src", 140)
    fieldsets = [
        (None, {"fields": ["clinic", "user", "is_active", "is_lead_doctor", "order"]}),
        ("Kimlik", {"fields": ["honorific", "name", "slug", ("photo", "photo_url", "photo_preview"), "specialties",
                               "languages_spoken"]}),
        ("Eğitim & üyelik (E-E-A-T)", {"fields": ["university", "graduation_year", "diploma_number", "memberships"]}),
        ("İçerik (kaynak dil)", {"fields": ["source_language", "auto_translate", "title_display", "bio",
                                            "meta_title", "meta_description", "translation_matrix"]}),
    ]

    @admin.display(description="")
    def thumb(self, obj):
        return format_html('<img src="{}" class="dt-thumb">', obj.photo_src) if obj.photo_src else "👩‍⚕️"
    inlines = [DoctorTranslationInline]


@admin.register(Review)
class ReviewAdmin(OwnerScopedMixin, admin.ModelAdmin):
    autocomplete_fields = ["treatment"]
    list_display = ["author_name", "country_code", "stars", "source_badge", "clinic", "treatment",
                    "is_verified_patient", "is_published", "is_featured", "created_at"]
    list_filter = ["is_published", "source", "rating", "is_verified_patient", "clinic", "language"]
    list_editable = ["is_published", "is_featured"]
    search_fields = ["author_name", "text", "email"]
    readonly_fields = ["created_at", "ip_hash"]
    actions = ["approve", "unpublish"]
    fieldsets = [
        (None, {"fields": ["clinic", "doctor", "treatment", "source", "source_url", "is_published", "is_featured",
                           "order"]}),
        ("Yorum", {"fields": ["author_name", "country_code", "language", "rating", "title", "text", "video_id",
                              "review_date", "treatment_date"]}),
        ("Doğrulama (sadece admin görür)", {"fields": ["email", "is_verified_patient", "lead", "ip_hash",
                                                       "created_at"]}),
        ("Klinik yanıtı", {"fields": ["reply", "reply_at"]}),
    ]
    raw_id_fields = ["lead"]

    @admin.display(description="Puan", ordering="rating")
    def stars(self, obj):
        return "★" * obj.rating

    @admin.display(description="Kaynak", ordering="source")
    def source_badge(self, obj):
        color = "#065f46" if obj.is_internal else "#475569"
        if obj.source_url:
            return format_html('<a href="{}" target="_blank" style="color:{}">{} ↗</a>', obj.source_url, color,
                               obj.get_source_display())
        return format_html('<span style="color:{}">{}</span>', color, obj.get_source_display())

    @admin.action(description="✅ Onayla ve yayınla")
    def approve(self, request, queryset):
        n = queryset.update(is_published=True)
        self.message_user(request, f"{n} yorum yayınlandı.")

    @admin.action(description="⛔ Yayından kaldır")
    def unpublish(self, request, queryset):
        queryset.update(is_published=False)

    def save_model(self, request, obj, form, change):
        from django.utils import timezone

        if obj.reply and not obj.reply_at:
            obj.reply_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(BeforeAfterCase)
class BeforeAfterCaseAdmin(OwnerScopedMixin, admin.ModelAdmin):
    list_display = ["before_thumb", "after_thumb", "clinic", "treatment", "caption", "patient_consent", "is_published"]
    list_filter = ["clinic", "is_published", "patient_consent"]
    readonly_fields = ["before_preview", "after_preview"]
    before_preview = image_preview("before_src", 180, "Önce")
    after_preview = image_preview("after_src", 180, "Sonra")
    fields = ["clinic", "doctor", "treatment", ("before_image", "before_image_url", "before_preview"),
              ("after_image", "after_image_url", "after_preview"),
              "caption", "patient_consent", "is_published", "order"]

    @admin.display(description="Önce")
    def before_thumb(self, obj):
        return format_html('<img src="{}" class="dt-thumb">', obj.before_src) if obj.before_src else "—"

    @admin.display(description="Sonra")
    def after_thumb(self, obj):
        return format_html('<img src="{}" class="dt-thumb">', obj.after_src) if obj.after_src else "—"
