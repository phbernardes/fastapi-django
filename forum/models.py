import uuid

from django.conf import settings
from django.db import models


class Post(models.Model):
    pubkey = models.UUIDField(
        default=uuid.uuid4, db_index=True, editable=False, unique=True
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        get_latest_by = "-created_at"
