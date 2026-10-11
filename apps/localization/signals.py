"""Kayıtlı içerik modelleri kaydedildiğinde otomatik çeviriyi tetikler."""
from django.conf import settings
from django.db.models.signals import post_save


def _on_save(sender, instance, raw=False, **kwargs):
    if raw or not settings.AUTO_TRANSLATE_ON_PUBLISH:
        return
    from .registry import get_spec
    from .service import sync_object

    spec = get_spec(sender)
    if spec and spec.should_auto_translate(instance):
        sync_object(instance)


def connect_all():
    from .registry import all_specs

    for spec in all_specs().values():
        post_save.connect(_on_save, sender=spec.model, dispatch_uid=f"autotranslate-{spec.model._meta.label_lower}")
