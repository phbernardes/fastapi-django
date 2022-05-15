import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pubkey = models.UUIDField(
        default=uuid.uuid4, db_index=True, editable=False, unique=True
    )

    EMAIL_FIELD = "username"
    USERNAME_FIELD = "username"

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"
