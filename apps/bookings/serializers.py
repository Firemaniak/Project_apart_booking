from .models import Booking
from rest_framework import serializers
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class BookingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'start_date', 'end_date', 'price', 'payment_type',
                  'guests_count', 'guest', 'listing', 'status', 'created_at']
        read_only_fields = ['price', 'status']


#----------------------              ------------------------------              ---------------------------------------


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'payment_type', 'guests_count', 'listing']

    def validate(self, attrs):
        if attrs['start_date'] >= attrs['end_date']:
            raise serializers.ValidationError('The end date must be later than the start date.')

        if attrs['start_date'].date() < timezone.localtime(timezone.now()).date():
            raise serializers.ValidationError('Start date cannot be in the past.')

        overlapping = Booking.objects.filter(
            listing=attrs['listing'],
            status='paid',
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


#-----------------------------------------------------------------------------------------------------------------------


class PaymentSerializer(serializers.Serializer):
    cardholder_name = serializers.CharField(max_length=100)
    card_number = serializers.CharField(max_length=19, write_only=True)
    expiry_date = serializers.CharField(max_length=5, write_only=True)  # MM/YY
    cvv = serializers.CharField(max_length=4, write_only=True)

    def validate_card_number(self, value):
        digits = value.replace(' ', '').replace('-', '')
        if not digits.isdigit() or len(digits) < 13 or len(digits) > 19:
            raise serializers.ValidationError('Invalid card number.')
        return digits

    def validate_expiry_date(self, value):
        import re
        if not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', value):
            raise serializers.ValidationError('Expiry date must be in MM/YY format.')

        from datetime import datetime
        month, year = value.split('/')
        expiry = datetime(2000 + int(year), int(month), 1)
        if expiry < datetime.now().replace(day=1):
            raise serializers.ValidationError('Card has expired.')
        return value

    def validate_cvv(self, value):
        if not value.isdigit() or len(value) not in (3, 4):
            raise serializers.ValidationError('Invalid CVV.')
        return value

    def validate_cardholder_name(self, value):
        if len(value.strip().split()) < 2:
            raise serializers.ValidationError('Enter full name (first and last name).')
        return value