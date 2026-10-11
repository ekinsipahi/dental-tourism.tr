"""Persona / dönüşüm paneli — /api/dashboard/ (sadece staff)."""
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render

from . import bandit
from .models import MLModelVersion, PersonaArmStat, PersonaExposure, VisitorSession


def _data():
    sessions = VisitorSession.objects.all()
    total = sessions.count()
    converted = sessions.filter(converted=True).count()
    segments = (PersonaArmStat.objects.exclude(segment=bandit.GLOBAL)
                .values("segment").annotate(n=Count("id")).order_by("segment"))
    seg_rows = []
    for seg in segments:
        arms = PersonaArmStat.objects.filter(segment=seg["segment"]).order_by("-conversions")
        seg_rows.append({"segment": seg["segment"], "arms": list(arms)})
    return {
        "total_sessions": total,
        "converted": converted,
        "conversion_rate": round(converted / total * 100, 2) if total else 0,
        "exposures": PersonaExposure.objects.count(),
        "arms": bandit.summary(),
        "segments": seg_rows,
        "inferred_vs_shown": list(PersonaExposure.objects.values("inferred_persona", "persona")
                                  .annotate(n=Count("id"), conv=Count("id", filter=Q(converted=True)))
                                  .order_by("-n")[:30]),
        "by_query": list(sessions.exclude(search_query="").values("search_query", "assigned_persona")
                         .annotate(n=Count("id")).order_by("-n")[:20]),
        "models": MLModelVersion.objects.all()[:10],
    }


@staff_member_required
def dashboard(request):
    from django.contrib import admin

    return render(request, "persona/dashboard.html", {**admin.site.each_context(request), **_data(),
                                                      "title": "Persona paneli"})


@staff_member_required
def funnel(request):
    s = VisitorSession.objects.all()
    return JsonResponse({
        "visitors": s.count(),
        "engaged": s.filter(total_page_views__gte=2).count(),
        "considered": s.filter(total_time_spent_sec__gte=60).count(),
        "interested": s.filter(cta_clicks__gte=1).count(),
        "converted": s.filter(converted=True).count(),
    })


@staff_member_required
def personas(request):
    return JsonResponse({"arms": [{k: v for k, v in a.items() if k != "alpha_beta"} for a in bandit.summary()]})
