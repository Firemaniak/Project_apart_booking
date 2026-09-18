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
    guests_count = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)],
                                                    verbose_name='number of guests'
    )
    payment_type = models.CharField(max_length=10,
                                    choices=PayTypeChoices, default=PayTypeChoices.bank_cart,
                                  verbose_name='payment type')
    prepayment_type = models.CharField(max_length=20,
                                       choices=PrepaymentTypeChoices, default=PrepaymentTypeChoices.partial_prepayment,
                                  verbose_name='prepayment type')
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')  ####ForeignKey HIERRRR---+++++
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name='bookings')  ####ForeignKey HIERRRR---+++++

    history = HistoricalRecords()

    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.guest} — {self.listing} ({self.start_date:%d.%m.%Y} – {self.end_date:%d.%m.%Y})'


    #Date validation
    def clean(self):
        super().clean()
        if self.start_date >= self.end_date:
            raise ValidationError("The end date must be later than the start date.")

        nights = (self.end_date.date() - self.start_date.date()).days
        if nights < 1:
            raise ValidationError("Booking must be at least one night.")

        if self.guests_count > self.listing.room_count * 2:
            raise ValidationError("Too many guests for this listing.")

        overlapping = Booking.objects.filter(
            listing=self.listing,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date,
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("This listing is already booked for the selected dates.")

    def save(self, *args, **kwargs):
        if not self.price:
            nights = (self.end_date.date() - self.start_date.date()).days
            self.price = self.listing.price_per_night * nights
        super().save(*args, **kwargs)




