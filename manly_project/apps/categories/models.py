from django.db import models
import uuid

class Category(models.Model):
    uuid = models.UUIDField(default =uuid.uuid4,editable=False,unique=True)
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
