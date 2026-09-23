# from django.conf import settings
#
#
# from django.db import models
#
# from django.utils.translation import gettext_lazy as _
#
# from apps.core.models import UniqueID, TimeStampedModel
# from apps.listings.models import Listing
#
# from django.core.validators import MinValueValidator, MaxValueValidator
#
# from django.core.exceptions import ValidationError
# from django.utils import timezone
#
#
# # -----------------------------------------------------------------------------------------------------------------------
#
# class ListingStatistic(UniqueID, TimeStampedModel):
#     view_count = models.PositiveIntegerField(default=0)
#     booking_count = models.PositiveIntegerField(default=0)
#     total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
#     reviews_count = models.PositiveIntegerField(default=0)
#     listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='statistic')
#
#
#
#     class Meta:
#         db_table = 'listing_statistics'
#         verbose_name = 'Listing statistic'
#         verbose_name_plural = 'Listing statistics'
#
#     def __str__(self):
#         return f'Stats for {self.listing.apartment_name}'
#
#
# #-------------------------                    ----------------------                   ---------------------------------
#
#
# class UserStatistic(UniqueID, TimeStampedModel):
#     booking_count = models.PositiveIntegerField(default=0)
#     listing_count = models.PositiveIntegerField(default=0)
#     stars_count = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
#     total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='statistic')
#
#
#     class Meta:
#         db_table = 'user_statistics'
#         verbose_name = 'User statistic'
#         verbose_name_plural = 'User statistics'
#
#     def __str__(self):
#         return f'Stats for {self.user.username}'
#
#
#
#
# class SearchHistory(UniqueID, TimeStampedModel):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
#                              related_name='search_history', null=True, blank=True)
#     keyword = models.CharField(max_length=100)
#
#     class Meta:
#         db_table = 'search_history'
#         verbose_name = 'Search history entry'
#         verbose_name_plural = 'Search history'
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return f'{self.keyword} ({self.created_at:%d.%m.%Y})'
#
#
# class ListingView(UniqueID, TimeStampedModel):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
#                              related_name='listing_views', null=True, blank=True)
#     listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='view_history')
#
#     class Meta:
#         db_table = 'listing_views'
#         verbose_name = 'Listing view'
#         verbose_name_plural = 'Listing views'
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return f'View of {self.listing.apartment_name} at {self.created_at:%d.%m.%Y %H:%M}'


from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Review
from .serializers import ReviewListSerializer, ReviewCreateSerializer, ReviewOwnerResponseSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    Public list of all reviews, and review creation.

    Anyone can read reviews (``IsAuthenticatedOrReadOnly``); creating
    one requires authentication, with the additional guest/timing
    checks enforced in ``ReviewCreateSerializer``.

    Публичный список всех отзывов и их создание.

    Читать отзывы может кто угодно (``IsAuthenticatedOrReadOnly``);
    для создания нужна авторизация, а дополнительные проверки
    (гость/сроки) выполняются в ``ReviewCreateSerializer``.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewListSerializer


class ReviewDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single review by id. Public — no authentication
    required, since reviews are meant to be visible to any visitor
    browsing a listing.

    Получение одного отзыва по id. Публично — авторизация не
    требуется, так как отзывы должны быть видны любому посетителю,
    просматривающему листинг.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.AllowAny]


class ReviewOwnerResponseView(generics.UpdateAPIView):
    """
    Lets a listing's owner respond to a review left on their listing.

    Ownership of the reviewed listing is validated inside
    ``ReviewOwnerResponseSerializer``, not here — permission_classes
    only checks that *some* user is authenticated.

    Позволяет владельцу листинга ответить на отзыв, оставленный на
    его листинг.

    Проверка владения листингом, на который оставлен отзыв,
    выполняется внутри ``ReviewOwnerResponseSerializer``, а не здесь —
    permission_classes проверяет только то, что пользователь вообще
    авторизован.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewOwnerResponseSerializer
    permission_classes = [permissions.IsAuthenticated]