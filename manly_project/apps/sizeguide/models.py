from django.db import models


class SizeGuide(models.Model):
    size_name = models.CharField(
        max_length=5,
        unique=True
    )  

    chest_min = models.FloatField()
    chest_max = models.FloatField()

    shoulder_min = models.FloatField()
    shoulder_max = models.FloatField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.size_name
