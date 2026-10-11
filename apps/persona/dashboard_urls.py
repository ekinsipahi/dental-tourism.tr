from django.urls import path

from . import dashboard_views as v

urlpatterns = [
    path("", v.dashboard, name="dashboard"),
    path("funnel/", v.funnel, name="dashboard-funnel"),
    path("personas/", v.personas, name="dashboard-personas"),
]
