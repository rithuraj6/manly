import uuid
from django.db import migrations


def fill_product_uuid(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    for product in Product.objects.filter(uuid__isnull=True):
        product.uuid = uuid.uuid4()
        product.save(update_fields=["uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0002_product_uuid"),
    ]

    operations = [
        migrations.RunPython(fill_product_uuid),
    ]

