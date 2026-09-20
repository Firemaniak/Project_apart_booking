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




class SearchHistory(UniqueID, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='search_history', null=True, blank=True)
    keyword = models.CharField(max_length=100)

    class Meta:
        db_table = 'search_history'
        verbose_name = 'Search history entry'
        verbose_name_plural = 'Search history'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.keyword} ({self.created_at:%d.%m.%Y})'


class ListingView(UniqueID, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='listing_views', null=True, blank=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='view_history')

    class Meta:
        db_table = 'listing_views'
        verbose_name = 'Listing view'
        verbose_name_plural = 'Listing views'
        ordering = ['-created_at']

    def __str__(self):
        return f'View of {self.listing.apartment_name} at {self.created_at:%d.%m.%Y %H:%M}'
