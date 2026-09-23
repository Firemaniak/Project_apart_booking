from django.db import models

from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

from apps.listings.models import Listing
from django.core.exceptions import ValidationError

from apps.core.models import UniqueID, TimeStampedModel

from simple_history.models import HistoricalRecords


#-----------------------------------------------------------------------------------------------------------------------


class PayTypeChoices(models.TextChoices):

    """
    Available payment methods for a booking.

    Доступные способы оплаты бронирования.
    """

    cash = 'cash', _('Cash')
    bank_cart = 'bank_cart', _('Bank_cart')
    kripto = 'kripto', _('Kripto')


class BookingStatusChoices(models.TextChoices):

    """
    Lifecycle status of a booking, from creation to completion.

    Статус жизненного цикла брони — от создания до завершения.
    """

    pending = 'pending', _('Pending payment')
    paid = 'paid', _('Paid')
    cancelled = 'cancelled', _('Cancelled')
    completed = 'completed', _('Completed')


#-----------------------------------------------------------------------------------------------------------------------


class Booking(TimeStampedModel, UniqueID):

    """
    A guest's reservation of a listing for a given date range.

    Price is calculated automatically from the listing's nightly rate
    and is not accepted from the client. Overlapping bookings for the
    same listing are rejected, and guests cannot book their own listing
    (enforced at the serializer level, since that check requires the
    request context).

    Бронь гостя на конкретный листинг на заданный диапазон дат.

    Цена рассчитывается автоматически на основе цены за сутки
    и не принимается от клиента. Пересекающиеся по датам брони на
    один и тот же листинг отклоняются; хозяин не может забронировать
    собственный листинг (проверяется на уровне сериализатора, так как
    там доступен контекст запроса).
    """

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
    status = models.CharField(max_length=10, choices=BookingStatusChoices, default=BookingStatusChoices.pending)

    card_last4 = models.CharField(max_length=4, blank=True)

    guest = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')

    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name='bookings')

    history = HistoricalRecords()

    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-start_date']


    def __str__(self):
        return f'{self.guest} — {self.listing} ({self.start_date:%d.%m.%Y} – {self.end_date:%d.%m.%Y})'


    def clean(self):

        """
        Validate booking dates, guest count, and availability.

        Checks that: the end date is after the start date, the stay is
        at least one night, the guest count does not exceed the listing's
        capacity, and the listing is not already booked for overlapping
        dates.

        Проверяет корректность дат брони, количество гостей и доступность.

        Проверяется: дата окончания позже даты начала, длительность
        не менее одной ночи, количество гостей не превышает вместимость
        листинга, и листинг не забронирован на пересекающиеся даты.
        """

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

        """
        Auto-calculate the price from the listing's nightly rate if not
        already set, so the client cannot supply an arbitrary price.

        Автоматически рассчитывает цену на основе стоимости за сутки,
        если она ещё не задана — чтобы клиент не мог передать
        произвольную цену.
        """

        if not self.price:
            nights = (self.end_date.date() - self.start_date.date()).days
            self.price = self.listing.price_per_night * nights
        super().save(*args, **kwargs)
