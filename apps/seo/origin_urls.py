from django.urls import path

from . import package_views as views

app_name = "origins"
urlpatterns = [
    path("<slug:country>/", views.package_origin, name="detail"),
]
