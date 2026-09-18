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
        fields = ['start_date', 'end_date', 'payment_type', 'prepayment_type', 'guests_count', 'listing']

    def validate(self, attrs):
        if attrs['start_date'] >= attrs['end_date']:
            raise serializers.ValidationError('The end date must be later than the start date.')

        if attrs['start_date'].date() < timezone.localtime(timezone.now()).date():
            raise serializers.ValidationError('Start date cannot be in the past.')

        overlapping = Booking.objects.filter(
            listing=attrs['listing'],
            start_date__lt=attrs['end_date'],
            end_date__gt=attrs['start_date'],
        )
        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)

        if overlapping.exists():
            raise serializers.ValidationError('This listing is already booked for the selected dates.')

        if attrs['guests_count'] > attrs['listing'].max_guests:
            raise serializers.ValidationError(
                f"This listing allows up to {attrs['listing'].max_guests} guests."
            )

        request = self.context.get('request')
        if request and attrs['listing'].owner == request.user:
            raise serializers.ValidationError("You can't book your own listing.")

        return attrs