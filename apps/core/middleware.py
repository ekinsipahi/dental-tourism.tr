import re

BOT_RE = re.compile(
    r"bot|crawl|spider|slurp|bingpreview|facebookexternalhit|embedly|quora link preview|"
    r"whatsapp|telegrambot|discordbot|linkedinbot|pinterest|vkshare|w3c_validator|lighthouse|"
    r"pagespeed|gtmetrix|headless|python-requests|curl|wget|ahrefs|semrush|mj12|dotbot|petalbot|"
    r"yandex|baiduspider|duckduckbot|applebot|gptbot|claudebot|ccbot|perplexity|"
    # UA'sında "bot" geçmeyen tarayıcılar / araçlar (canlı veride oturum açtıkları görüldü, 2026-11):
    r"googleother|google-inspectiontool|storebot|prefetch proxy|go-http-client|rust_sniffer|skypeuripreview|"
    r"okhttp|python|java/|libwww|scrapy|httpclient|axios|node-fetch|postmanruntime|insomnia|httpx|aiohttp|"
    r"phantomjs|puppeteer|playwright|selenium|chrome-lighthouse|dataprovider|screaming frog|siteaudit|"
    r"semrushbot|seokicks|serpstat|netcraft|archive\.org|ia_archiver|bytespider|amazonbot|meta-externalagent",
    re.I,
)


class BotDetectionMiddleware:
    """request.is_bot — botlar için tracking/persona DB yazımı yapılmaz ve
    her zaman varsayılan (SEO) içerik gösterilir."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ua = request.META.get("HTTP_USER_AGENT", "")
        # Tarayıcı imzası olmayan ya da yalnızca "Mozilla/5.0" gibi kırpık UA'lar da bot sayılır (gerçek tarayıcılar
        # AppleWebKit / Gecko / Trident içerir); bunlar JS çalıştırmadığı için zaten hiç beacon göndermiyordu.
        request.is_bot = (not ua or bool(BOT_RE.search(ua))
                          or not any(sig in ua for sig in ("AppleWebKit", "Gecko", "Trident", "Opera")))
        return self.get_response(request)


class BotPageCacheMiddleware:
    """Botlara (Googlebot, Bing, Ahrefs … → request.is_bot) hazır sayfayı süreç içi bellekten verir.

    Neden güvenli: botlar için zaten oturum açılmaz, takip/persona çalışmaz ve herkes aynı varsayılan (SEO) içeriği
    görür (PERSONA_UI kapalı). Dolayısıyla aynı (dil, yol) için üretilen HTML her bot için aynıdır.
    Kazanç: 1200 URL × her tarama = ~40-50 Supabase sorgusu → 0 (6 saat boyunca). Sayfalar zlib ile sıkıştırılıp
    "local" önbelleğe (LocMem, commit öneki → her deploy'da sıfırlanır) yazılır; ~15 KB × en çok 4000 giriş.
    Yalnızca: GET, query string yok, 200 + text/html, Set-Cookie yok, /admin /api dışı."""

    SKIP = ("/admin", "/api/", "/static/", "/media/")
    TTL = 60 * 60 * 6

    def __init__(self, get_response):
        self.get_response = get_response

    def _key(self, request):
        return f"bot:{getattr(request, 'LANGUAGE_CODE', '')}:{request.path}"

    def __call__(self, request):
        cacheable = (getattr(request, "is_bot", False) and request.method == "GET" and not request.GET
                     and not request.path.startswith(self.SKIP))
        if not cacheable:
            return self.get_response(request)
        import zlib

        from django.core.cache import caches
        from django.http import HttpResponse

        cache = caches["local"]
        hit = cache.get(self._key(request))
        if hit is not None:
            content_type, blob = hit
            resp = HttpResponse(zlib.decompress(blob), content_type=content_type)
            resp["X-Bot-Cache"] = "HIT"
            return resp
        response = self.get_response(request)
        ctype = response.get("Content-Type", "")
        if (response.status_code == 200 and ctype.startswith("text/html") and not response.has_header("Set-Cookie")
                and not getattr(response, "streaming", False)):
            cache.set(self._key(request), (ctype, zlib.compress(response.content, 6)), self.TTL)
            response["X-Bot-Cache"] = "MISS"
        return response
