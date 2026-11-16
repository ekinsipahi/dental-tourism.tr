from django.urls import path

from .external import ext_event, ext_lead, ext_pageview

urlpatterns = [
    path("pageview/", ext_pageview, name="t-pageview"),
    path("event/", ext_event, name="t-event"),
    path("lead/", ext_lead, name="t-lead"),
]
