from .models import ListingStatistic, UserStatistic
from rest_framework import serializers
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class ListingStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingStatistic
        fields = ['listing', 'views_count', 'bookings_count', 'total_revenue',
                  'average_rating', 'reviews_count']


class UserStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatistic
        fields = ['user', 'bookings_count', 'listings_count', 'stars_count',
                  'total_earned', 'total_spent']