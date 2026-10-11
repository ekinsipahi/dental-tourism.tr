from django.urls import path

from . import views

app_name = "doctors"
urlpatterns = [
    path("<slug:slug>/", views.doctor_detail, name="detail"),
]
