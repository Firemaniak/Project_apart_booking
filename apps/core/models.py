import uuid
from django.db import models


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