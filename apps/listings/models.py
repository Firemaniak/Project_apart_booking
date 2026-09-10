#from django.contrib.auth.models import User
from django.db import models
import uuid

from django.db.models.fields import CharField, DecimalField
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.conf import settings

from apps.users.models import User


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


class Input_type(models.TextChoices):
    with_key = 'key', _('Key')
    with_pin_kode = 'pin_kode', _('Pin_kode')
    with_card = 'card', _('Card')


#-----------------------------------------------------------------------------------------------------------------------


class Listing(UniqueID, TimeStampedModel):
    apartment_name = models.CharField(validators=[MinLengthValidator(3),MaxLengthValidator(30)],
                                  verbose_name='apartment name')
    discription = models.TextField(blank=True,
                                   verbose_name='discription')
    address = models.CharField(validators=[MinLengthValidator(5),MaxLengthValidator(40)],
                                 verbose_name='address')
    floor = models.CharField(validators=[MinLengthValidator(1),MaxLengthValidator(165)],
                                 verbose_name='floor')    #Бурдж-Халифа в Дубае, ОАЭ имеет 163 этажа
    country = models.CharField(validators=[MinLengthValidator(2),MaxLengthValidator(20)],
                                 verbose_name='country')
    room_count = models.CharField(validators=[MinLengthValidator(1),MaxLengthValidator(20)],
                                 verbose_name='number of rooms')
    shower_count = models.CharField(validators=[MinLengthValidator(1), MaxLengthValidator(20)],
                                  verbose_name='number of shower rooms')
    toilets_count = models.CharField(validators=[MinLengthValidator(1), MaxLengthValidator(20)],
                                    verbose_name='number of toilets')
    input_type = models.CharField(choices=Input_type, default=Input_type.with_key,
                                  verbose_name='how to get in')
    parking = models.BooleanField(default=False,
                                  verbose_name='availability of parking')
    can_smoke = models.BooleanField(default=False,
                                    verbose_name='Is smoking allowed?')
    wifi = models.BooleanField(default=False,
                               verbose_name= 'Wi-Fi')
    indoor_fireplace = models.BooleanField(default=False,
                                           verbose_name='Is there a fireplace')
    can_pets = models.BooleanField(default=False,
                                   verbose_name='Are pets allowed?')
    facilities_for_guests_with_disabilities = models.BooleanField(default=False,
                                                                  verbose_name='Accessibility for people with '
                                                                               'disabilities?')
    air_conditioner = models.BooleanField(default=False,
                                          verbose_name='Is there air conditioning?')
    elevator = models.BooleanField(default=False,
                                   verbose_name='Is there an elevator?')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings') ####ForeignKey HIERRRR---+++++


    def __str__(self):
        return f'User: {apartment_name}, {room_count}, {country}'


    class Meta:
        db_table = 'listings'
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        ordering = ['apartment_name', 'country', 'room_count']


#-----------------------------------------------------------------------------------------------------------------------
