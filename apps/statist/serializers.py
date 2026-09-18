from .models import ListingStatistic, UserStatistic
from rest_framework import serializers
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class ListingStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingStatistic
        fields = ['listing', 'view_count', 'booking_count', 'total_revenue',
                  'average_rating', 'reviews_count']


class UserStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatistic
        fields = ['user', 'booking_count', 'listing_count', 'stars_count',]