from django.urls import path

from . import area_views as views

app_name = "areas"
urlpatterns = [
    path("", views.area_index, name="index"),
    path("<slug:area>/", views.area_detail, name="detail"),
]
