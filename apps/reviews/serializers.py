from .models import Review
from rest_framework import serializers
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class ReviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'comment', 'booking', 'stars', 'owner_response', 'owner_response_at', 'created_at']




class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['comment', 'booking', 'stars']



    def validate(self, attrs):
        booking = attrs['booking']

        if booking.end_date > timezone.now():
            raise serializers.ValidationError('You can leave a review only after the booking is finished.')

        request = self.context.get('request')
        if request and booking.guest != request.user:
            raise serializers.ValidationError("You can only review your own bookings.")

        return attrs



class ReviewOwnerResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['owner_response']

    def validate(self, attrs):
        request = self.context.get('request')
        review = self.instance  # объект уже существует — это Update, не Create

        if request and review.booking.listing.owner != request.user:
            raise serializers.ValidationError("Only the listing owner can respond to this review.")

        return attrs

    def update(self, instance, validated_data):
        instance.owner_response = validated_data['owner_response']
        instance.owner_response_at = timezone.now()
        instance.save()
        return instance