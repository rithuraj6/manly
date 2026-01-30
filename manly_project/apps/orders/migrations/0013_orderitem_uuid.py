from django.db import migrations, models
import uuid


def populate_orderitem_uuid(apps, schema_editor):
    OrderItem = apps.get_model("orders", "OrderItem")
    for item in OrderItem.objects.filter(uuid__isnull=True):
        item.uuid = uuid.uuid4()
        item.save(update_fields=["uuid"])

class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0012_order_uuid"),  # keep correct previous migration
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="uuid",
            field=models.UUIDField(null=True, unique=True),
        ),
        migrations.RunPython(populate_orderitem_uuid),
        migrations.AlterField(
            model_name="orderitem",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
