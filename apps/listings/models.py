from django.db import models

from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
from django.conf import settings

from apps.core.models import UniqueID, TimeStampedModel

from simple_history.models import HistoricalRecords


#-----------------------------------------------------------------------------------------------------------------------

class InputTypeChoices(models.TextChoices):
    with_key = 'key', _('Key')
    with_pin_kode = 'pin_kode', _('Pin_kode')
    with_card = 'card', _('Card')


#-----------------------------------------------------------------------------------------------------------------------


class Listing(UniqueID, TimeStampedModel):
    apartment_name = models.CharField(max_length=30, validators=[MinLengthValidator(3),MaxLengthValidator(30)],
                                  verbose_name='apartment name')
    description = models.TextField(blank=True,
                                   verbose_name='description')
    address = models.CharField(max_length=60, validators=[MinLengthValidator(5)],
                                 verbose_name='address')
    floor = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(165)],
                                 verbose_name='floor')    #Бурдж-Халифа в Дубае, ОАЭ имеет 163 этажа
    country = models.CharField(max_length=30, validators=[MinLengthValidator(2)],
                                 verbose_name='country')
    room_count = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(20)],
                                 verbose_name='number of rooms')
    shower_count = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)],
                                  verbose_name='number of shower rooms')
    toilets_count = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)],
                                    verbose_name='number of toilets')
    input_type = models.CharField(max_length=10, choices=InputTypeChoices, default=InputTypeChoices.with_key,
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

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                              related_name='listings') ###ForeignKey HIERRRR---+++++

    photo = models.ImageField(upload_to='listing_photo/', blank=True, null=True)

    price_per_night = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='price per night'
    )

    history = HistoricalRecords()



    def __str__(self):
        return f'Apartment: {self.apartment_name}, {self.country}, {self.room_count} rooms'


    class Meta:
        db_table = 'listings'
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        ordering = ['apartment_name', 'country', 'room_count']


#-----------------------------------------------------------------------------------------------------------------------
