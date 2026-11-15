from django.urls import path

from .external import ext_event, ext_pageview

urlpatterns = [
    path("pageview/", ext_pageview, name="t-pageview"),
    path("event/", ext_event, name="t-event"),
]
