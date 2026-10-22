from apps.persona.models import PERSONA_UNKNOWN

SKIP_PREFIXES = ("/static/", "/media/", "/api/", "/admin/", "/favicon", "/robots.txt", "/sitemap", "/site.webmanifest", "/apple-touch-icon", "/llms.txt")
DEFAULT = {"persona": PERSONA_UNKNOWN, "confidence": 0.0, "theme_class": "theme-default", "is_known": False}


class PersonaMiddleware:
    """Her sayfa isteğinde persona kararını request.persona'ya koyar."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(SKIP_PREFIXES) or request.method != "GET":
            request.persona = dict(DEFAULT)
            return self.get_response(request)
        from apps.tracking import visitor

        if not getattr(request, "is_bot", False):
            visitor.ensure_visitor_id(request)
        try:
            from .engine import get_or_create_persona

            request.persona = get_or_create_persona(request)
        except Exception:  # noqa: BLE001 — kişiselleştirme asla sayfayı düşürmemeli
            import logging

            logging.getLogger(__name__).exception("persona engine failed")
            request.persona = dict(DEFAULT)
        response = self.get_response(request)
        visitor.set_cookie(request, response)
        if hasattr(request, "_persona_preview"):  # ?persona= önizlemesi (staff/DEBUG) — imzalı çerez, oturum değil
            from .engine import PREVIEW_COOKIE, PREVIEW_MAX_AGE, PREVIEW_SALT

            if request._persona_preview:
                response.set_signed_cookie(PREVIEW_COOKIE, request._persona_preview, salt=PREVIEW_SALT,
                                           max_age=PREVIEW_MAX_AGE, httponly=True, samesite="Lax")
            else:
                response.delete_cookie(PREVIEW_COOKIE)
        if request.persona.get("is_known"):
            response.headers["Vary"] = ", ".join(filter(None, [response.headers.get("Vary"), "Cookie"]))
        return response
