from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    chest = models.FloatField(null=True, blank=True)
    shoulder = models.FloatField(null=True, blank=True)

    size = models.CharField(max_length=5, blank=True)

    def calculate_size(self):
        if not self.chest:
            return ""

        if self.chest < 90:
            return "S"
        elif self.chest < 100:
            return "M"
        elif self.chest < 110:
            return "L"
        else:
            return "XL"
