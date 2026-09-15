from .models import Listing
from rest_framework import serializers
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class ListingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'apartment_name', 'country', 'address', 'max_guests', 'parking', 'elevator', 'price_per_night']


class ListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = [
            'apartment_name', 'description', 'address', 'floor', 'country',
            'room_count', 'shower_count', 'toilets_count', 'max_guests', 'input_type',
            'parking', 'can_smoke', 'wifi', 'indoor_fireplace', 'can_pets',
            'facilities_for_guests_with_disabilities', 'air_conditioner', 'elevator',
            'photo', 'price_per_night',
        ]




