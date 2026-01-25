from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("coupons", "0002_remove_coupon_end_date_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CouponUsage",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("used_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="used_coupons",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "coupon",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="usages",
                        to="coupons.coupon",
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "coupon")},
            },
        ),
    ]
