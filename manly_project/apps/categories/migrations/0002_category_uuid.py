from django.db import migrations, models
import uuid


def generate_category_uuids(apps, schema_editor):
    Category = apps.get_model("categories", "Category")
    for category in Category.objects.all():
        if not category.uuid:
            category.uuid = uuid.uuid4()
            category.save(update_fields=["uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0001_initial"),
    ]

    operations = [
        
        migrations.AddField(
            model_name="category",
            name="uuid",
            field=models.UUIDField(null=True, editable=False),
        ),

      
        migrations.RunPython(generate_category_uuids),

        migrations.AlterField(
            model_name="category",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False,
            ),
        ),
    ]
