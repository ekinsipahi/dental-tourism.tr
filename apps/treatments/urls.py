from django.urls import path

from apps.seo import views as seo_views

from . import views

app_name = "treatments"
urlpatterns = [
    path("", views.treatment_list, name="list"),
    path("<slug:slug>/", views.treatment_detail, name="detail"),
    path("<slug:slug>/<slug:city_slug>/", seo_views.treatment_city, name="city"),
]
