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
        from .models import Redirect

        r = Redirect.objects.filter(old_path=request.path).first()
        if r is None:
            return response
        Redirect.objects.filter(pk=r.pk).update(hits=F("hits") + 1)
        cls = HttpResponsePermanentRedirect if r.permanent else HttpResponseRedirect
        return cls(r.new_path)
