# from .models import Review
# from rest_framework import serializers
# from django.utils import timezone
#
#
# #-----------------------------------------------------------------------------------------------------------------------
#
#
# class ReviewListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Review
#         fields = ['id', 'comment', 'booking', 'stars', 'owner_response', 'owner_response_at', 'created_at']
#
#
#
#
# class ReviewCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Review
#         fields = ['comment', 'booking', 'stars']
#
#
#
#     def validate(self, attrs):
#         booking = attrs['booking']
#
#         if booking.end_date > timezone.now():
#             raise serializers.ValidationError('You can leave a review only after the booking is finished.')
#
#         request = self.context.get('request')
#         if request and booking.guest != request.user:
#             raise serializers.ValidationError("You can only review your own bookings.")
#
#         return attrs
#
#
#
# class ReviewOwnerResponseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Review
#         fields = ['owner_response']
#
#     def validate(self, attrs):
#         request = self.context.get('request')
#         review = self.instance  # объект уже существует — это Update, не Create
#
#         if request and review.booking.listing.owner != request.user:
#             raise serializers.ValidationError("Only the listing owner can respond to this review.")
#
#         return attrs
#
#     def update(self, instance, validated_data):
#         instance.owner_response = validated_data['owner_response']
#         instance.owner_response_at = timezone.now()
#         instance.save()
#         return instance
#


from .models import Review
from rest_framework import serializers
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class ReviewListSerializer(serializers.ModelSerializer):
    """
    Read-only representation of a review, including the host's
    response if one was given.

    Представление отзыва для чтения, включая ответ хозяина,
    если он был дан.
    """
    class Meta:
        model = Review
        fields = ['id', 'comment', 'booking', 'stars', 'owner_response', 'owner_response_at', 'created_at']




class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Validates and creates a review for a completed booking.

    Only the guest who made the booking can review it, and only after
    the stay has actually ended — mirrors ``Review.clean()`` at the
    serializer level, since DRF does not call full_clean() automatically.

    Валидирует и создаёт отзыв на завершённую бронь.

    Оставить отзыв может только гость, сделавший эту бронь, и только
    после того, как проживание реально закончилось — дублирует
    ``Review.clean()`` на уровне сериализатора, так как DRF не вызывает
    full_clean() автоматически.
    """
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
    """
    Lets a listing's owner post a public response to a guest's review.

    Used only for updates (PATCH on an existing review), never for
    creation — a response is always attached to a review that already
    exists.

    Позволяет владельцу листинга опубликовать ответ на отзыв гостя.

    Используется только для обновления (PATCH на существующем отзыве),
    никогда для создания — ответ всегда привязывается к уже
    существующему отзыву.
    """
    class Meta:
        model = Review
        fields = ['owner_response']

    def validate(self, attrs):
        """
        Only the owner of the listing being reviewed may respond —
        not the reviewer, and not any other user.

        Ответить может только владелец листинга, на который оставлен
        отзыв — не сам автор отзыва и не любой другой пользователь.
        """
        request = self.context.get('request')
        review = self.instance  # объект уже существует — это Update, не Create

        if request and review.booking.listing.owner != request.user:
            raise serializers.ValidationError("Only the listing owner can respond to this review.")

        return attrs

    def update(self, instance, validated_data):
        """
        Set the response text and timestamp it automatically — the
        client only supplies the text, never the timestamp.

        Устанавливает текст ответа и автоматически проставляет
        метку времени — клиент передаёт только текст, но не время.
        """
        instance.owner_response = validated_data['owner_response']
        instance.owner_response_at = timezone.now()
        instance.save()
        return instance