# from django.db import models
#
# from django.utils.translation import gettext_lazy as _
#
# from apps.core.models import UniqueID, TimeStampedModel
# from apps.bookings.models import Booking
#
# from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
#
# from django.core.exceptions import ValidationError
# from django.utils import timezone
#
#
# #-----------------------------------------------------------------------------------------------------------------------
#
#
# # class StarsChoices(models.TextChoices):
# #     one_star = 'one', _('One')
# #     two_stars = 'two', _('Two')
# #     three_stars = 'three', _('Three')
# #     four_stars = 'four', _('Four')
# #     five_stars = 'five', _('Five')
# #     no_stars = 'no_stars', _('No_stars')
#
#
#
#
# class Review(UniqueID, TimeStampedModel):
#     comment = models.TextField(validators=[MinLengthValidator(10)])
#     booking = models.OneToOneField(Booking, on_delete=models.PROTECT,
#                                           related_name='review')
#     stars = models.PositiveSmallIntegerField(
#         validators=[MinValueValidator(1), MaxValueValidator(5)],
#         verbose_name='stars')
#     owner_response = models.TextField(blank=True)
#     owner_response_at = models.DateTimeField(blank=True, null=True)
#
#
#     def __str__(self):
#         return f'{self.booking.guest} — {self.stars}★'
#
#
#     class Meta:
#         db_table = 'reviews'
#         verbose_name = 'Review'
#         verbose_name_plural = 'Reviews'
#         ordering = ['-created_at']
#
#
#     #проверка что комент можно оставить только после окончания брони
#     def clean(self):
#         super().clean()
#         if self.booking.end_date > timezone.localtime(timezone.now()):
#             raise ValidationError('Оставить отзыв можно только после завершения бронирования.')
#




from django.db import models

from django.utils.translation import gettext_lazy as _

from apps.core.models import UniqueID, TimeStampedModel
from apps.bookings.models import Booking

from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator

from django.core.exceptions import ValidationError
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class Review(UniqueID, TimeStampedModel):
    """
    A guest's review of a completed booking, with an optional public
    response from the host.

    ``booking`` is a OneToOneField — a booking can have at most one
    review, and ``on_delete=PROTECT`` prevents deleting a booking that
    already has a review attached. ``owner_response_at`` is set
    automatically when the host adds a response (see the review
    signal/save logic).

    Отзыв гостя на завершённую бронь, с опциональным публичным ответом
    хозяина.

    ``booking`` — это OneToOneField: у одной брони может быть не более
    одного отзыва, а ``on_delete=PROTECT`` не даёт удалить бронь,
    у которой уже есть привязанный отзыв. ``owner_response_at``
    проставляется автоматически, когда хозяин добавляет ответ (см.
    логику сигнала/save для отзыва).
    """
    comment = models.TextField(validators=[MinLengthValidator(10)])
    booking = models.OneToOneField(Booking, on_delete=models.PROTECT,
                                          related_name='review')
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='stars')
    owner_response = models.TextField(blank=True)
    owner_response_at = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return f'{self.booking.guest} — {self.stars}★'


    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']


    def clean(self):
        """
        A review can only be left once the booking's stay has actually
        ended — prevents guests from reviewing a stay before it happens.

        Отзыв можно оставить только после того, как проживание по
        брони реально завершилось — не даёт гостю оставить отзыв
        до фактического проживания.
        """
        super().clean()
        if self.booking.end_date > timezone.localtime(timezone.now()):
            raise ValidationError('Оставить отзыв можно только после завершения бронирования.')
