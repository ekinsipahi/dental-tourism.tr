from django.contrib.admin.apps import AdminConfig


class DentalAdminConfig(AdminConfig):
    """django.contrib.admin yerine — özel DentalAdminSite'ı varsayılan admin.site yapar."""
    default_site = "apps.core.admin_site.DentalAdminSite"
