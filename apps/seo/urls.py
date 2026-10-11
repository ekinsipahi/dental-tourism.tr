from django.urls import path

from . import views

app_name = "prices"
urlpatterns = [
    path("", views.price_index, name="index"),
    path("<slug:slug>/", views.treatment_price, name="detail"),
]
