def persona_context(request):
    persona = getattr(request, "persona", None) or {
        "persona": "unknown", "theme_class": "theme-default", "confidence": 0.0, "is_known": False,
    }
    return {"persona": persona}
