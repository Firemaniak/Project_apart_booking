from django.db import models

from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

from apps.listings.models import Listing
from django.core.exceptions import ValidationError

from apps.core.models import UniqueID, TimeStampedModel

from simple_history.models import HistoricalRecords


#-----------------------------------------------------------------------------------------------------------------------


class PrepaymentTypeChoices(models.TextChoices):
    free_booking = 'free_booking', _('Free_booking')
    partial_prepayment = 'partial_prepayment', _('Partial_prepayment')
    full_payment = 'full_payment', _('Full_payment')

class PayTypeChoices(models.TextChoices):
    cash = 'cash', _('Cash')
    bank_cart = 'bank_cart', _('Bank_cart')
    kripto = 'kripto', _('Kripto')


#-----------------------------------------------------------------------------------------------------------------------


class Booking(TimeStampedModel, UniqueID):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)],
                                verbose_name='price')
    payment_type = models.CharField(choices=PayTypeChoices, default=PayTypeChoices.bank_cart,
                                  verbose_name='payment type')
    prepayment_type = models.CharField(choices=PrepaymentTypeChoices, default=PrepaymentTypeChoices.partial_prepayment,
                                  verbose_name='prepayment type')
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')  ####ForeignKey HIERRRR---+++++
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name='bookings')  ####ForeignKey HIERRRR---+++++

    history = HistoricalRecords()


    #Date validation
    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("The end date must be later than the start date.")




