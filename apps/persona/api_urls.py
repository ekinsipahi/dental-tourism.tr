from django.urls import path
from .api_views import collect_event, persona_status
urlpatterns = [
    path("event/", collect_event, name="persona-event"),
    path("status/", persona_status, name="persona-status"),
]
