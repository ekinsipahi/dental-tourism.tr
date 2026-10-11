from django.urls import path

from . import guide_views as views

app_name = "guides"
urlpatterns = [
    path("", views.guide_index, name="index"),
    path("<slug:slug>/", views.guide_detail, name="detail"),
]
