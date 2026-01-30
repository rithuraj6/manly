import uuid
from django.db import migrations, models


def populate_address_uuids(apps, schema_editor):
    UserAddress = apps.get_model("accounts", "UserAddress")
    for address in UserAddress.objects.all():
        address.uuid = uuid.uuid4()
        address.save(update_fields=["uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_emailotp_attempts_emailotp_is_blocked_and_more"),  # 👈 Django already filled this
    ]

    operations = [
        migrations.AddField(
            model_name="useraddress",
            name="uuid",
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.RunPython(populate_address_uuids),
        migrations.AlterField(
            model_name="useraddress",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                unique=True,
            ),
        ),
    ]
