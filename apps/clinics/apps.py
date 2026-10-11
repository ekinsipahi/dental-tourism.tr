from django.apps import AppConfig


class ClinicsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.clinics"
    label = "clinics"
    verbose_name = "Clinics & Doctors"

    def ready(self):
        from django.db.models.signals import post_save

        from .models import Review
        from .review_translate import on_review_saved

        post_save.connect(on_review_saved, sender=Review, dispatch_uid="review-autotranslate")
