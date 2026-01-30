import uuid
from django.db import migrations, models


def populate_offer_uuids(apps, schema_editor):
    Offer = apps.get_model("offers", "Offer")
    for offer in Offer.objects.all():
        offer.uuid = uuid.uuid4()
        offer.save(update_fields=["uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ("offers", "0001_initial"),  # keep Django’s value
    ]

    operations = [
        migrations.AddField(
            model_name="offer",
            name="uuid",
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.RunPython(populate_offer_uuids),
        migrations.AlterField(
            model_name="offer",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False
            ),
        ),
    ]
