from django.db import migrations, models
import uuid


def generate_order_uuids(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    for order in Order.objects.all():
        if not order.uuid:
            order.uuid = uuid.uuid4()
            order.save(update_fields=["uuid"])


class Migration(migrations.Migration):

    dependencies = [
    ("orders", "0011_order_coupon_order_coupon_discount"),
    ]

    operations = [
        
        migrations.AddField(
            model_name="order",
            name="uuid",
            field=models.UUIDField(null=True, editable=False),
        ),

        migrations.RunPython(generate_order_uuids),

        migrations.AlterField(
            model_name="order",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False,
            ),
        ),
    ]
