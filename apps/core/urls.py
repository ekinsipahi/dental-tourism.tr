from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "core"
urlpatterns = [
    path("", views.home, name="home"),
    path(_("about/"), views.about, name="about"),
    path(_("contact/"), views.contact, name="contact"),
    path(_("contact/thank-you/"), views.thanks, name="thanks"),
    path(_("privacy/"), views.privacy, name="privacy"),
]
