from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


#-----------------------------------------------------------------------------------------------------------------------


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar', 'date_joined']


#---------------------------               --------------------------                   --------------------------------


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'birth_date', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # хеширует пароль, не хранит plain text
        user.save()
        return user



# apps/users/serializers.py
class UserProfileSerializer(serializers.ModelSerializer):
    total_earned = serializers.DecimalField(source='statistic.total_earned', max_digits=12, decimal_places=2,
                                            read_only=True)
    total_spent = serializers.DecimalField(source='statistic.total_spent', max_digits=12, decimal_places=2,
                                           read_only=True)
    booking_count = serializers.IntegerField(source='statistic.booking_count',
                                             read_only=True)
    listing_count = serializers.IntegerField(source='statistic.listing_count',
                                             read_only=True)
    stars_count = serializers.DecimalField(source='statistic.stars_count', max_digits=3, decimal_places=2,
                                           read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'birth_date', 'bio', 'address', 'phone', 'avatar',
                  'total_earned', 'total_spent', 'booking_count', 'listing_count', 'stars_count']
        read_only_fields = ['id', 'username']