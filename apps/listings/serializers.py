from .models import Listing, Photo, Favorite, PropertyTypeChoices
from rest_framework import serializers
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'image', 'listing']


    def validate_listing(self, value):
        request = self.context.get('request')
        if request and value.owner != request.user:
            raise serializers.ValidationError("You can only add photos to your own listings.")
        return value


class ListingListSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'apartment_name', 'country', 'address', 'max_guests', 'parking', 'elevator', 'price_per_night',
                  'property_type', 'photos', 'owner', 'owner_username', 'is_active', 'latitude', 'longitude']


class ListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = [
            'apartment_name', 'description', 'address', 'floor', 'floors_count', 'country',
            'room_count', 'shower_count', 'toilets_count', 'max_guests', 'input_type',
            'parking', 'can_smoke', 'wifi', 'indoor_fireplace', 'can_pets',
            'facilities_for_guests_with_disabilities', 'air_conditioner', 'elevator',
            'price_per_night', 'property_type', 'is_active', 'latitude', 'longitude'
        ]

    def validate(self, attrs):
        property_type = attrs.get('property_type', PropertyTypeChoices.apartment)
        if property_type == 'house':
            if not attrs.get('floors_count'):
                raise serializers.ValidationError({'floors_count': 'Required for houses.'})
        else:
            if not attrs.get('floor'):
                raise serializers.ValidationError({'floor': 'Required for apartments and rooms.'})
        return attrs



#----------------------------------------------------------------------------------------------------------------



class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'listing', 'created_at']

