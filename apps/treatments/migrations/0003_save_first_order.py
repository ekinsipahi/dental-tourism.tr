"""Tedavi sırası: önce dişi koruyan tedaviler, implant ve All-on-4 en sonda ("save the natural tooth first")."""
from django.db import migrations

ORDER = ["root-canal", "tooth-filling", "teeth-cleaning", "composite-veneers", "teeth-whitening",
         "zirconia-crowns", "porcelain-veneers", "hollywood-smile", "dental-implants", "all-on-4"]


def forwards(apps, schema_editor):
    Treatment = apps.get_model("treatments", "Treatment")
    for i, key in enumerate(ORDER, 1):
        Treatment.objects.filter(key=key).update(order=i)


class Migration(migrations.Migration):
    dependencies = [("treatments", "0002_treatment_image_url")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
