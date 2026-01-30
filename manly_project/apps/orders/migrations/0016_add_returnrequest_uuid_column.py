from django.db import migrations, models
import uuid


def populate_missing_uuids(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    OrderItem = apps.get_model("orders", "OrderItem")
    ReturnRequest = apps.get_model("orders", "ReturnRequest")
    Payment = apps.get_model("orders", "Payment")

    for model in [Order, OrderItem, ReturnRequest, Payment]:
        for obj in model.objects.all():
            if not getattr(obj, "uuid", None):
                obj.uuid = uuid.uuid4()
                obj.save(update_fields=["uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0015_alter_payment_uuid_alter_returnrequest_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="returnrequest",
            name="uuid",
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name="payment",
            name="uuid",
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(populate_missing_uuids),
        migrations.AlterField(
            model_name="returnrequest",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                unique=True,
            ),
        ),
    ]
