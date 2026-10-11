from django.urls import path

from . import package_views as views

app_name = "packages"
urlpatterns = [
    path("", views.package_index, name="index"),
    path("<slug:slug>/", views.package_treatment, name="treatment"),
]
