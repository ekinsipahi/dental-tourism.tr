from django.db import migrations, models


def set_brand(apps, schema_editor):
    Doctor = apps.get_model("clinics", "Doctor")
    Doctor.objects.filter(slug="devrim-biriken-sipahi", brand_name="").update(brand_name="Dr. Devrim")


class Migration(migrations.Migration):
    dependencies = [("clinics", "0007_beforeaftercase_key_beforeaftercase_title_and_more")]
    operations = [
        migrations.AddField(
            model_name="doctor", name="brand_name",
            field=models.CharField(blank=True, max_length=60,
                                   help_text='Pazarlama adı (ör. "Dr. Devrim"). Sitede öne çıkar; tam ad altında görünür.'),
        ),
        migrations.RunPython(set_brand, migrations.RunPython.noop),
    ]
