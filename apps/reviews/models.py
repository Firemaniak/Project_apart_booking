#from django.contrib.auth.models import User
from django.db import models
import uuid

from django.db.models.fields import CharField, DecimalField
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.conf import settings

from apps.users.models import Booking


#-----------------------------------------------------------------------------------------------------------------------


class UniqueID(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4,
                          verbose_name='UUID id')

    class Meta:
        abstract = True

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


#-----------------------------------------------------------------------------------------------------------------------

class Reviews(UniqueID, TimeStampedModel):
    pass
