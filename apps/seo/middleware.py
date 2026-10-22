from django.db.models import F
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect


class RedirectFallbackMiddleware:
    """404 olan istekler için Redirect tablosuna bakar (slug değişikliği, eski site URL'leri)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != 404:
            return response
        from django.core.cache import caches

        from .models import Redirect

        # Tablo küçük: 5 dakikada bir okunur (tarayıcı botlarının her 404'ünde Supabase'e gitmesin)
        table = caches["local"].get("redirects:map")
        if table is None:
            table = {old: (new, perm, pk) for old, new, perm, pk in Redirect.objects.values_list("old_path", "new_path", "permanent", "pk")}
            caches["local"].set("redirects:map", table, 300)
        hit = table.get(request.path)
        if hit is None:
            return response
        new_path, permanent, pk = hit
        Redirect.objects.filter(pk=pk).update(hits=F("hits") + 1)
        cls = HttpResponsePermanentRedirect if permanent else HttpResponseRedirect
        return cls(new_path)
