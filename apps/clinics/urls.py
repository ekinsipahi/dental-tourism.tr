from django.urls import path

from . import views

app_name = "clinics"
urlpatterns = [
    path("", views.clinic_list, name="list"),
    path("<slug:slug>/", views.clinic_detail, name="detail"),
    path("<slug:slug>/review/", views.submit_review, name="review"),
]
