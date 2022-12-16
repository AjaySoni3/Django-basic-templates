from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

from .managers import CustomUserManager
import uuid


# Create your models here.

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, )
    email = models.EmailField(_('email address'), unique=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Types(models.TextChoices):
        Reader = "Reader", "READER"
        Author = "Author", "AUTHOR"

    default_type = Types.Reader

    user_type = MultiSelectField(choices=Types.choices,
                                 default=[],
                                 max_choices=2,
                                 max_length=255,
                                 null=True,
                                 blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.id:
            self.user_type = self.default_type
        return super().save(*args, **kwargs)
