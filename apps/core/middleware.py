import re

BOT_RE = re.compile(
    r"bot|crawl|spider|slurp|bingpreview|facebookexternalhit|embedly|quora link preview|"
    r"whatsapp|telegrambot|discordbot|linkedinbot|pinterest|vkshare|w3c_validator|lighthouse|"
    r"pagespeed|gtmetrix|headless|python-requests|curl|wget|ahrefs|semrush|mj12|dotbot|petalbot|"
    r"yandex|baiduspider|duckduckbot|applebot|gptbot|claudebot|ccbot|perplexity",
    re.I,
)


class BotDetectionMiddleware:
    """request.is_bot — botlar için tracking/persona DB yazımı yapılmaz ve
    her zaman varsayılan (SEO) içerik gösterilir."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ua = request.META.get("HTTP_USER_AGENT", "")
        request.is_bot = not ua or bool(BOT_RE.search(ua))
        return self.get_response(request)
