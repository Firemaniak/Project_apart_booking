from .models import ListingStatistic, UserStatistic
from rest_framework import serializers
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class ListingStatisticSerializer(serializers.ModelSerializer):

    """
    Public statistics for a single listing: views, bookings, revenue,
    and rating. Kept up to date by signals in ``apps.statist.signals``,
    not computed on the fly.

    Публичная статистика по одному листингу: просмотры, брони,
    выручка, рейтинг. Поддерживается в актуальном состоянии сигналами
    в ``apps.statist.signals``, а не вычисляется "на лету".
    """

    class Meta:
        model = ListingStatistic
        fields = ['listing', 'view_count', 'booking_count', 'total_revenue',
                  'average_rating', 'reviews_count']


class UserStatisticSerializer(serializers.ModelSerializer):

    """
    Public statistics for a user (as host): listing/booking counts and
    rating. Deliberately excludes financial fields (total_earned,
    total_spent) — those are only exposed on the user's own profile,
    never to other users viewing a public profile.

    Публичная статистика пользователя (как хозяина): количество
    листингов/броней и рейтинг. Намеренно не включает финансовые поля
    (заработано, потрачено) — они видны только самому пользователю
    в своём профиле, но не другим при просмотре публичного профиля.
    """

    class Meta:
        model = UserStatistic
        fields = ['user', 'booking_count', 'listing_count', 'stars_count',]