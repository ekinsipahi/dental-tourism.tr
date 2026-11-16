from django.urls import path

from .external import ext_event, ext_lead, ext_pageview, ext_persona

urlpatterns = [
    path("pageview/", ext_pageview, name="t-pageview"),
    path("event/", ext_event, name="t-event"),
    path("persona/", ext_persona, name="t-persona"),
    path("lead/", ext_lead, name="t-lead"),
]
