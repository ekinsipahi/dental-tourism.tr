from django.urls import path
from .views import (
    collect_event, collect_pageview, submit_lead,
    whatsapp_webhook, session_status, dashboard_stats,
)

urlpatterns = [
    path("event/",            collect_event,    name="tracking-event"),
    path("pageview/",         collect_pageview, name="tracking-pageview"),
    path("lead/",             submit_lead,      name="tracking-lead"),
    path("whatsapp-webhook/", whatsapp_webhook, name="tracking-wa-webhook"),
    path("session/",          session_status,   name="tracking-session"),
    path("dashboard/",        dashboard_stats,  name="tracking-dashboard"),
]
