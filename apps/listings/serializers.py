from .models import Listing, Photo, Favorite, PropertyTypeChoices
from rest_framework import serializers
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class PhotoSerializer(serializers.ModelSerializer):
    """
    Handles a single photo upload and its attachment to a listing.

    Обрабатывает загрузку одной фотографии и её привязку к листингу.
    """
    class Meta:
        model = Photo
        fields = ['id', 'image', 'listing']


    def validate_listing(self, value):
        """
        Only the owner of a listing may add photos to it — prevents
        one user from attaching photos to someone else's listing.

        Добавлять фото к листингу может только его владелец — не
        позволяет одному пользователю прикреплять фото к чужому
        листингу.
        """
        request = self.context.get('request')
        if request and value.owner != request.user:
            raise serializers.ValidationError("You can only add photos to your own listings.")
        return value


class ListingListSerializer(serializers.ModelSerializer):
    """
    Full read representation of a listing, used for both the catalog
    and the detail page.

    Полное представление листинга для чтения — используется и для
    каталога, и для страницы деталей.
    """
    photos = PhotoSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'apartment_name', 'description', 'country', 'address', 'floor', 'floors_count',
                  'room_count', 'shower_count', 'toilets_count', 'max_guests', 'input_type',
                  'parking', 'can_smoke', 'wifi', 'indoor_fireplace', 'can_pets',
                  'facilities_for_guests_with_disabilities', 'air_conditioner', 'elevator',
                  'price_per_night', 'property_type', 'photos', 'owner', 'owner_username',
                  'is_active', 'latitude', 'longitude']


class ListingCreateSerializer(serializers.ModelSerializer):
    """
    Validates and creates/updates a listing. Reused for both creation
    (POST) and editing (PUT/PATCH), since both actions accept the same
    set of fields.

    ``owner`` is intentionally excluded — it is set from the
    authenticated request user in the view, not accepted from the
    client.

    Валидирует и создаёт/обновляет листинг. Переиспользуется и для
    создания (POST), и для редактирования (PUT/PATCH), так как оба
    действия принимают один и тот же набор полей.

    Поле ``owner`` намеренно отсутствует — оно проставляется из
    авторизованного пользователя во вьюхе, а не принимается от
    клиента.
    """
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
        """
        Mirror the model's clean() rule at the serializer level, since
        DRF does not call full_clean() automatically: houses require
        floors_count, other property types require floor.

        Дублирует правило из clean() модели на уровне сериализатора,
        так как DRF не вызывает full_clean() автоматически: для домов
        обязателен floors_count, для остальных типов жилья — floor.
        """
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
    """
    Represents a user's bookmarked listing.

    ``user`` is excluded from the fields — it is set from the
    authenticated request user in the view, so a user can only
    favorite listings on their own behalf.

    Представляет закладку пользователя на листинг.

    Поле ``user`` отсутствует в списке полей — оно проставляется из
    авторизованного пользователя во вьюхе, чтобы добавлять в избранное
    можно было только от своего имени.
    """
    class Meta:
        model = Favorite
        fields = ['id', 'listing', 'created_at']
