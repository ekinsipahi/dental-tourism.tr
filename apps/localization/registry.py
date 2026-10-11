"""
Çevrilebilir model kaydı.

Her içerik modeli bir TranslationSpec ile kaydedilir; servis bu bilgiyle
AI çeviri şemasını, prompt bağlamını ve kayıt mantığını üretir.

    @register
    class TreatmentSpec(TranslationSpec):
        model = Treatment
        fields = [Field("name"), Field("slug", "slug"), Field("body", "markdown"), ...]
"""
from dataclasses import dataclass

from django.conf import settings

_REGISTRY: dict = {}


@dataclass
class Field:
    name: str
    kind: str = "text"          # text | markdown | slug | keyword | faq | list
    instructions: str = ""
    max_length: int | None = None


class TranslationSpec:
    model = None
    fields: list = []
    #: Prompt'ta içeriğin ne olduğunu anlatır
    content_kind = "web page"

    # ── Davranış kancaları ────────────────────────────────────────────────
    def should_auto_translate(self, obj) -> bool:
        """Kaydedildiğinde otomatik çeviri tetiklensin mi?"""
        return getattr(obj, "auto_translate", True)

    def target_languages(self, obj) -> list:
        return [c for c, _ in settings.LANGUAGES if c != obj.source_language]

    def dependencies(self, obj) -> list:
        """Bu nesneyle birlikte çevrilmesi gereken diğer nesneler (ör. yazının kategorisi)."""
        return []

    def extra_context(self, obj, lang) -> str:
        """Prompt'a eklenecek, nesneye/dile özel bağlam."""
        return ""

    # ── Yardımcılar ───────────────────────────────────────────────────────
    @property
    def translation_model(self):
        return self.model.translations.rel.related_model

    @property
    def parent_fk(self):
        return self.model.translations.field.name

    def field(self, name):
        return next((f for f in self.fields if f.name == name), None)

    def json_schema(self) -> dict:
        props, required = {}, []
        for f in self.fields:
            if f.kind == "faq":
                props[f.name] = {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"question": {"type": "string"}, "answer": {"type": "string"}},
                        "required": ["question", "answer"],
                        "additionalProperties": False,
                    },
                }
            elif f.kind == "list":
                props[f.name] = {"type": "array", "items": {"type": "string"}}
            else:
                props[f.name] = {"type": "string"}
            required.append(f.name)
        return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


def register(spec_cls):
    spec = spec_cls()
    _REGISTRY[spec.model._meta.label_lower] = spec
    return spec_cls


def get_spec(obj_or_model):
    model = obj_or_model if isinstance(obj_or_model, type) else type(obj_or_model)
    return _REGISTRY.get(model._meta.label_lower)


def get_spec_by_label(label):
    return _REGISTRY.get(label.lower())


def all_specs():
    return dict(_REGISTRY)
