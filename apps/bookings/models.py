#from django.contrib.auth.models import User
from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.conf import settings

from apps.users.models import User, Listing
from django.core.exceptions import ValidationError


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


class Prepaymenttype(models.TextChoices):
    free_booking = 'free_booking', _('Free_booking')
    partial_prepayment = 'partial_prepayment', _('Partial_prepayment')
    full_payment = 'full_payment', _('Full_payment')

class Paytype(models.TextChoices):
    cash = 'cash', _('Cash')
    bank_cart = 'bank_cart', _('Bank_cart')
    kripto = 'kripto', _('Kripto')


#-----------------------------------------------------------------------------------------------------------------------


class Booking(TimeStampedModel, UniqueID):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(choices=Paytype, default=Paytype.bank_cart,
                                  verbose_name='payment type')
    prepayment_type = models.CharField(choices=Prepaymenttype, default=Prepaymenttype.partial_prepayment,
                                  verbose_name='prepayment type')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')  ####ForeignKey HIERRRR---+++++
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')  ####ForeignKey HIERRRR---+++++


    #Date validation
    def clean(self):
        if self.stast_date >= self.end_date:
            raise ValidationError("The end date must be later than the start date.")




