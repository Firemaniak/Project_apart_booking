from .models import Booking
from rest_framework import serializers
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class BookingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'start_date', 'end_date', 'price', 'payment_type',
                  'prepayment_type', 'guests_count', 'guest', 'listing', 'created_at']
        read_only_fields = ['price']


#----------------------              ------------------------------              ---------------------------------------


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'start_date', 'end_date', 'payment_type', 'prepayment_type', 'guests_count', 'listing']



