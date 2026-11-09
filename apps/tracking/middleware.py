import logging

logger = logging.getLogger(__name__)

SKIP_PREFIXES = ("/static/", "/media/", "/favicon", "/admin/", "/robots.txt", "/sitemap", "/site.webmanifest",
                 "/apple-touch-icon", "/llms.txt")


class TrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tracking_session = None
        if getattr(request, "is_bot", False) or request.path.startswith(SKIP_PREFIXES):
            return self.get_response(request)
        try:
            from . import visitor
            from .service import attach_lazy_session

            visitor.ensure_visitor_id(request)  # ilk istekte de kalıcı kimlik (çerez PersonaMiddleware yanıtında yazılır)
            attach_lazy_session(request)  # DB'ye gidilmez; oturum ilk JS beacon'ında (pageview/event) açılır
        except Exception as e:  # noqa: BLE001
            logger.warning("TrackingMiddleware error: %s", e)
        return self.get_response(request)
