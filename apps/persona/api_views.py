import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def collect_event(request):
    """Geriye uyumluluk — yeni tracker tek endpoint (/api/tracking/event/) kullanır."""
    if getattr(request, "is_bot", False) or not request.session.session_key:
        return JsonResponse({"ok": True})
    try:
        body = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False}, status=400)
    from .engine import record_event

    record_event(request.session.session_key, str(body.get("event_type", ""))[:30], body.get("data") or {},
                 str(body.get("page_url", "")), str(body.get("page_type", "")))
    return JsonResponse({"ok": True})


def persona_status(request):
    from .engine import get_or_create_persona

    p = get_or_create_persona(request)
    return JsonResponse({k: p.get(k) for k in ("persona", "inferred", "confidence", "theme_class", "is_known", "method")})
