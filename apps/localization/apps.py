from django.apps import AppConfig


class LocalizationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.localization"
    label = "localization"
    verbose_name = "Localization / AI Translation"

    def ready(self):
        # Her app'in translation.py dosyasındaki TranslationSpec kayıtlarını yükle
        from django.utils.module_loading import autodiscover_modules

        from .signals import connect_all

        autodiscover_modules("translation")
        connect_all()
