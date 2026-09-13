from django.conf import settings


from django.db import models

from django.utils.translation import gettext_lazy as _

from apps.core.models import UniqueID, TimeStampedModel
from apps.listings.models import Listing

from django.core.validators import MinValueValidator, MaxValueValidator

from django.core.exceptions import ValidationError
from django.utils import timezone


# -----------------------------------------------------------------------------------------------------------------------

class ListingStatistic(UniqueID, TimeStampedModel):
    view_count = models.PositiveIntegerField(default=0)
    booking_count = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    reviews_count = models.PositiveIntegerField(default=0)
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='statistic')



    class Meta:
        db_table = 'listing_statistics'
        verbose_name = 'Listing statistic'
        verbose_name_plural = 'Listing statistics'

    def __str__(self):
        return f'Stats for {self.listing.apartment_name}'


#-------------------------                    ----------------------                   ---------------------------------


class UserStatistic(UniqueID, TimeStampedModel):
    booking_count = models.PositiveIntegerField(default=0)
    listing_count = models.PositiveIntegerField(default=0)
    stars_count = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='statistic')


    class Meta:
        db_table = 'user_statistics'
        verbose_name = 'User statistic'
        verbose_name_plural = 'User statistics'

    def __str__(self):
        return f'Stats for {self.user.username}'
