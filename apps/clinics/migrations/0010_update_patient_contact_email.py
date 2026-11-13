from django.db import migrations
from django.db.models import Value
from django.db.models.functions import Replace


def update_contact_email(apps, schema_editor):
    Clinic = apps.get_model("clinics", "Clinic")
    Clinic.objects.using(schema_editor.connection.alias).filter(
        slug="dr-devrim-sipahi",
    ).update(email="ekinsipahi8@gmail.com")
    for name in ("ContentBlock", "ContentBlockTranslation"):
        model = apps.get_model("core", name)
        for old in ("info@dentaltourism.tr", "ekinsipahi8@mail.com"):
            model.objects.using(schema_editor.connection.alias).filter(
                body__contains=old,
            ).update(body=Replace("body", Value(old), Value("ekinsipahi8@gmail.com")))


class Migration(migrations.Migration):
    dependencies = [
        ("clinics", "0009_doctor_instagram"),
        ("core", "0006_language_choices_bg"),
    ]

    operations = [migrations.RunPython(update_contact_email, migrations.RunPython.noop)]
